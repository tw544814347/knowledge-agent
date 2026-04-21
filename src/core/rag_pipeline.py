"""RAG Pipeline：检索增强生成核心流程编排"""

import asyncio
from typing import Iterator

from loguru import logger

from config.settings import settings
from src.core.document_loader import DocumentLoader
from src.core.document_processor import DocumentProcessor
from src.core.vector_store import VectorStore
from src.core.llm_client import LLMClient, LLMError
from src.core.web_search import fetch_web_snippets
from src.prompts.templates import SYSTEM_PROMPT, format_qa_prompt
from src.models.schemas import QueryResponse, SourceInfo


class RAGPipeline:
    """完整的 RAG 流程：索引 + 问答"""

    def __init__(self, vector_store: VectorStore | None = None):
        self.loader = DocumentLoader(settings.knowledge_source_dir)
        self.processor = DocumentProcessor()
        self.vector_store = vector_store or VectorStore()
        self.llm = LLMClient()

    def index_all(self) -> int:
        """全量索引：加载所有文档 → 切分 → 写入向量库"""
        logger.info("开始全量索引...")
        self.vector_store.clear()

        documents = self.loader.load_all()
        if not documents:
            logger.warning("未找到任何文档")
            return 0

        child_chunks, parent_map = self.processor.process_documents(documents)
        self.vector_store.add_documents(child_chunks, parent_map)

        logger.info(
            f"全量索引完成: {len(documents)} 个文档 → "
            f"{len(child_chunks)} 个检索 chunk + {len(parent_map)} 个上下文 chunk"
        )
        return len(child_chunks)

    def query(self, question: str, top_k: int | None = None, web_search: bool = False) -> QueryResponse:
        """
        RAG 问答：检索 → 构建 Prompt → LLM 生成

        @param question: 用户问题
        @param top_k: 检索 Top-K 数量
        @param web_search: 为 True 时，仅当知识库无命中才联网补充上下文
        @returns: 包含回答和来源信息的响应
        """
        _top_k = top_k or settings.top_k
        logger.info(f"收到问题: {question[:80]}")

        hits = self.vector_store.query(question, top_k=_top_k)
        web_snippets: list[dict] = []
        if web_search and not hits:
            web_snippets = fetch_web_snippets(question)

        prompt = format_qa_prompt(question, hits, web_snippets or None)
        answer = self.llm.generate(prompt, system_prompt=SYSTEM_PROMPT)

        sources = self._extract_sources(hits) + self._extract_web_sources(web_snippets)

        logger.info(f"回答生成完成，长度: {len(answer)}，引用 {len(sources)} 个来源")
        return QueryResponse(answer=answer, sources=sources, question=question)

    async def aquery(self, question: str, top_k: int | None = None, web_search: bool = False) -> QueryResponse:
        """异步版本的 RAG 问答"""
        _top_k = top_k or settings.top_k
        logger.info(f"收到异步问题: {question[:80]}")

        hits = self.vector_store.query(question, top_k=_top_k)
        web_snippets: list[dict] = []
        if web_search and not hits:
            web_snippets = await asyncio.to_thread(fetch_web_snippets, question)

        prompt = format_qa_prompt(question, hits, web_snippets or None)
        answer = await self.llm.agenerate(prompt, system_prompt=SYSTEM_PROMPT)

        sources = self._extract_sources(hits) + self._extract_web_sources(web_snippets)
        return QueryResponse(answer=answer, sources=sources, question=question)

    def stream_query(
        self, question: str, top_k: int | None = None, web_search: bool = False
    ) -> Iterator[dict]:
        """流式 RAG 问答：先返回 sources，再逐 token 返回 LLM 输出"""
        _top_k = top_k or settings.top_k
        logger.info(f"收到流式问题: {question[:80]} web_search={web_search}")

        hits = self.vector_store.query(question, top_k=_top_k)
        web_snippets: list[dict] = []
        if web_search and not hits:
            web_snippets = fetch_web_snippets(question)

        sources = self._extract_sources(hits) + self._extract_web_sources(web_snippets)

        yield {"type": "sources", "sources": [s.model_dump() for s in sources]}

        prompt = format_qa_prompt(question, hits, web_snippets or None)
        try:
            for token in self.llm.stream_generate(prompt, system_prompt=SYSTEM_PROMPT):
                yield {"type": "token", "content": token}
        except LLMError as e:
            yield {"type": "error", "message": str(e)}
            return

        yield {"type": "done"}

    @staticmethod
    def _extract_sources(hits: list[dict]) -> list[SourceInfo]:
        sources = []
        for hit in hits:
            meta = hit["metadata"]
            refs_to = meta.get("references_to", "")
            refs_by = meta.get("referenced_by", "")
            related = []
            if refs_to:
                related.extend(
                    r.strip().rsplit("/", 1)[-1]
                    for r in refs_to.split(",")
                    if r.strip()
                )
            if refs_by:
                related.extend(
                    r.strip().rsplit("/", 1)[-1]
                    for r in refs_by.split(",")
                    if r.strip()
                )

            sources.append(
                SourceInfo(
                    filename=meta.get("filename", "未知"),
                    category=meta.get("category", ""),
                    score=hit.get("score", 0.0),
                    section=meta.get("h2", meta.get("h1", "")),
                    related_docs=list(dict.fromkeys(related)),
                )
            )
        return sources

    @staticmethod
    def _extract_web_sources(web_snippets: list[dict]) -> list[SourceInfo]:
        out: list[SourceInfo] = []
        for w in web_snippets:
            title = (w.get("title") or "网页").strip()[:120]
            url = (w.get("url") or "").strip()
            out.append(
                SourceInfo(
                    filename=title,
                    category="网络",
                    score=0.0,
                    section=url[:500],
                    related_docs=[],
                )
            )
        return out
