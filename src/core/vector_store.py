"""向量存储模块：基于 ChromaDB + Ollama Embedding"""

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
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=8),
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.ConnectError)),
        reraise=True,
    )
    def _embed_single(self, text: str) -> list[float]:
        resp = self._client.post(
            f"{self.base_url}/api/embed",
            json={"model": self.model, "input": text},
        )
        resp.raise_for_status()
        data = resp.json()
        return data["embeddings"][0]

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """批量生成 Embedding（逐条调用 Ollama API）"""
        embeddings: list[list[float]] = []
        for text in texts:
            embedding = self._embed_single(text)
            embeddings.append(embedding)
        return embeddings

    def close(self) -> None:
        self._client.close()


class ChromaEmbeddingFunction:
    """ChromaDB 所需的 EmbeddingFunction 适配器"""

    def __init__(self, ollama_embedding: OllamaEmbedding):
        self._embed = ollama_embedding

    def __call__(self, texts: list[str]) -> list[list[float]]:
        return self._embed.embed_texts(texts)


class VectorStore:
    """ChromaDB 向量存储管理"""

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
        logger.info(
            f"向量库已就绪: {self.collection_name} "
            f"(已有 {self._collection.count()} 条记录)"
        )

    def add_documents(self, chunks: list[Document], batch_size: int = 50) -> None:
        """将 chunk 批量写入向量库"""
        total = len(chunks)
        for start in range(0, total, batch_size):
            batch = chunks[start : start + batch_size]
            ids = [f"{c.doc_id}_{c.metadata.get('chunk_index', start + i)}" for i, c in enumerate(batch)]
            documents = [c.content for c in batch]
            metadatas = [
                {k: str(v) for k, v in c.metadata.items()}
                for c in batch
            ]
            self._collection.upsert(
                ids=ids,
                documents=documents,
                metadatas=metadatas,
            )
            logger.debug(f"已写入 {min(start + batch_size, total)}/{total} 条")

        logger.info(f"向量库写入完成，共 {total} 条，当前总量 {self._collection.count()}")

    def query(self, query_text: str, top_k: int = settings.top_k) -> list[dict]:
        """相似度检索，返回 Top-K 相关 chunk"""
        results = self._collection.query(
            query_texts=[query_text],
            n_results=top_k,
            include=["documents", "metadatas", "distances"],
        )

        hits: list[dict] = []
        if results and results["documents"]:
            for doc, meta, dist in zip(
                results["documents"][0],
                results["metadatas"][0],
                results["distances"][0],
            ):
                hits.append({
                    "content": doc,
                    "metadata": meta,
                    "score": 1.0 - dist,
                })
        return hits

    def delete_by_source(self, source_path: str) -> None:
        """删除指定来源文件的所有 chunk"""
        self._collection.delete(where={"source": source_path})
        logger.info(f"已删除来源为 {source_path} 的文档")

    def clear(self) -> None:
        """清空整个 collection"""
        self._client.delete_collection(self.collection_name)
        self._collection = self._client.get_or_create_collection(
            name=self.collection_name,
            embedding_function=self._ef,
            metadata={"hnsw:space": "cosine"},
        )
        logger.info("向量库已清空")

    def close(self) -> None:
        self._embedding.close()

    @property
    def count(self) -> int:
        return self._collection.count()
