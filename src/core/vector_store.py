"""向量存储模块：基于 ChromaDB + Ollama Embedding

支持 Parent Document Retrieval、分数阈值过滤、同文件去重。
"""

from pathlib import Path

import chromadb
from chromadb.config import Settings as ChromaSettings
import httpx
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from config.settings import settings
from src.core.document_loader import Document


class OllamaEmbedding:
    """通过 Ollama REST API 生成 Embedding 向量"""

    def __init__(
        self,
        base_url: str = settings.ollama_base_url,
        model: str = settings.embedding_model,
    ):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self._client = httpx.Client(timeout=60.0)

    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, min=2, max=30),
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.ConnectError, RuntimeError)),
        reraise=True,
    )
    def _embed_single(self, text: str) -> list[float]:
        try:
            resp = self._client.post(
                f"{self.base_url}/api/embed",
                json={"model": self.model, "input": text},
            )
            resp.raise_for_status()
            data = resp.json()
            if "embeddings" not in data or not data["embeddings"]:
                raise RuntimeError(f"Ollama embed 响应缺少 embeddings 字段: {list(data.keys())}")
            return data["embeddings"][0]
        except httpx.HTTPStatusError as e:
            raise RuntimeError(f"Ollama embedding HTTP {e.response.status_code}") from e

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """批量生成 Embedding（逐条调用 Ollama API）"""
        return [self._embed_single(t) for t in texts]

    def close(self) -> None:
        self._client.close()


class ChromaEmbeddingFunction:
    """ChromaDB EmbeddingFunction 适配器"""

    def __init__(self, ollama_embedding: OllamaEmbedding):
        self._embed = ollama_embedding

    def __call__(self, input: list[str]) -> list[list[float]]:
        return self._embed.embed_texts(input)


class VectorStore:
    """ChromaDB 向量存储管理

    内置 Parent Document Retrieval：
    - 写入时同时存储 child chunks（用于检索）和 parent chunks（用于上下文）
    - 检索时命中 child → 返回对应 parent 的完整内容
    """

    def __init__(
        self,
        persist_dir: str | Path = settings.chroma_persist_dir,
        collection_name: str = settings.chroma_collection_name,
    ):
        self.persist_dir = str(persist_dir)
        self.collection_name = collection_name

        self._embedding = OllamaEmbedding()
        self._ef = ChromaEmbeddingFunction(self._embedding)

        self._client = chromadb.PersistentClient(
            path=self.persist_dir,
            settings=ChromaSettings(anonymized_telemetry=False),
        )
        self._collection = self._client.get_or_create_collection(
            name=self.collection_name,
            embedding_function=self._ef,
            metadata={"hnsw:space": "cosine"},
        )

        self._parent_collection = self._client.get_or_create_collection(
            name=f"{self.collection_name}_parents",
            embedding_function=self._ef,
        )
        logger.info(
            f"向量库已就绪: {self.collection_name} "
            f"(child={self._collection.count()}, "
            f"parent={self._parent_collection.count()})"
        )

    def add_documents(
        self,
        child_chunks: list[Document],
        parent_map: dict[str, Document],
        batch_size: int = 30,
    ) -> None:
        """写入 child chunks（可检索）和 parent chunks（仅存储）

        手动预计算 embedding 后再写入，绕过 ChromaDB 内部 embedding 调用的兼容性问题。
        """
        total = len(child_chunks)
        for start in range(0, total, batch_size):
            batch = child_chunks[start : start + batch_size]
            ids = [
                f"{c.doc_id}_{c.metadata.get('chunk_index', start + i)}"
                for i, c in enumerate(batch)
            ]
            documents = [c.content for c in batch]
            metadatas = [{k: str(v) for k, v in c.metadata.items()} for c in batch]
            embeddings = self._embedding.embed_texts(documents)
            self._collection.upsert(
                ids=ids, documents=documents, metadatas=metadatas, embeddings=embeddings
            )
            logger.debug(f"child 已写入 {min(start + batch_size, total)}/{total}")

        p_items = list(parent_map.items())
        for start in range(0, len(p_items), batch_size):
            batch = p_items[start : start + batch_size]
            p_ids = [pid for pid, _ in batch]
            p_docs = [doc.content for _, doc in batch]
            p_metas = [{k: str(v) for k, v in doc.metadata.items()} for _, doc in batch]
            p_embeddings = self._embedding.embed_texts(p_docs)
            self._parent_collection.upsert(
                ids=p_ids, documents=p_docs, metadatas=p_metas, embeddings=p_embeddings
            )
            logger.debug(f"parent 已写入 {min(start + batch_size, len(p_items))}/{len(p_items)}")

        logger.info(
            f"向量库写入完成: {total} child + {len(parent_map)} parent, "
            f"当前总量 child={self._collection.count()}, parent={self._parent_collection.count()}"
        )

    def query(
        self,
        query_text: str,
        top_k: int = settings.top_k,
        min_score: float = settings.min_score,
        max_per_doc: int = settings.max_chunks_per_doc,
    ) -> list[dict]:
        """
        检索流程：
        1. 用 query 在 child collection 中检索 top_k * 2 条候选
        2. 过滤低于 min_score 的结果
        3. 同一文件最多保留 max_per_doc 条
        4. 用 parent_id 查找完整上下文，替换 child content
        """
        query_embedding = self._embedding.embed_texts([query_text])[0]
        raw = self._collection.query(
            query_embeddings=[query_embedding],
            n_results=min(top_k * 3, self._collection.count() or 1),
            include=["documents", "metadatas", "distances"],
        )

        if not raw or not raw["documents"] or not raw["documents"][0]:
            return []

        candidates = []
        for doc, meta, dist in zip(
            raw["documents"][0], raw["metadatas"][0], raw["distances"][0]
        ):
            score = 1.0 - dist
            if score < min_score:
                continue
            candidates.append({"content": doc, "metadata": meta, "score": score})

        hits = self._dedup_by_file(candidates, max_per_doc)
        hits = hits[:top_k]

        self._resolve_parents(hits)

        return hits

    def _dedup_by_file(self, candidates: list[dict], max_per_doc: int) -> list[dict]:
        """同一文件只保留得分最高的 max_per_doc 个 chunk"""
        file_counts: dict[str, int] = {}
        result: list[dict] = []
        for c in candidates:
            fn = c["metadata"].get("filename", "")
            cnt = file_counts.get(fn, 0)
            if cnt < max_per_doc:
                result.append(c)
                file_counts[fn] = cnt + 1
        return result

    def _resolve_parents(self, hits: list[dict]) -> None:
        """将 child content 替换为其所属 parent chunk 的完整内容"""
        parent_ids = list({
            h["metadata"].get("parent_id", "")
            for h in hits
            if h["metadata"].get("parent_id")
        })
        if not parent_ids:
            return

        try:
            parents = self._parent_collection.get(
                ids=parent_ids, include=["documents"]
            )
            pid_to_content = {}
            if parents and parents["ids"]:
                for pid, pdoc in zip(parents["ids"], parents["documents"]):
                    pid_to_content[pid] = pdoc

            for h in hits:
                pid = h["metadata"].get("parent_id", "")
                if pid in pid_to_content:
                    h["child_content"] = h["content"]
                    h["content"] = pid_to_content[pid]
        except Exception as e:
            logger.warning(f"获取 parent chunk 失败（回退到 child）: {e}")

    def delete_by_source(self, source_path: str) -> None:
        """删除指定来源文件的所有 chunk"""
        self._collection.delete(where={"source": source_path})
        self._parent_collection.delete(where={"source": source_path})
        logger.info(f"已删除来源为 {source_path} 的文档")

    def clear(self) -> None:
        """清空所有 collection"""
        self._client.delete_collection(self.collection_name)
        self._collection = self._client.get_or_create_collection(
            name=self.collection_name,
            embedding_function=self._ef,
            metadata={"hnsw:space": "cosine"},
        )

        parent_name = f"{self.collection_name}_parents"
        try:
            self._client.delete_collection(parent_name)
        except ValueError:
            logger.debug(f"parent collection '{parent_name}' 不存在，跳过删除")
        self._parent_collection = self._client.get_or_create_collection(
            name=parent_name,
            embedding_function=self._ef,
        )
        logger.info("向量库已清空（child + parent）")

    def close(self) -> None:
        self._embedding.close()

    @property
    def count(self) -> int:
        return self._collection.count()

    @property
    def parent_count(self) -> int:
        return self._parent_collection.count()
