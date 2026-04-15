"""RAG Pipeline：检索增强生成核心流程编排"""

from loguru import logger

from config.settings import settings
from src.core.document_loader import DocumentLoader
from src.core.document_processor import DocumentProcessor
from src.core.vector_store import VectorStore
from src.core.llm_client import LLMClient
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

        chunks = self.processor.process_documents(documents)
        self.vector_store.add_documents(chunks)

        logger.info(f"全量索引完成: {len(documents)} 个文档 → {len(chunks)} 个 chunk")
        return len(chunks)

    def query(self, question: str, top_k: int | None = None) -> QueryResponse:
        """
        RAG 问答：检索 → 构建 Prompt → LLM 生成

        @param question: 用户问题
        @param top_k: 检索 Top-K 数量
        @returns: 包含回答和来源信息的响应
        """
        _top_k = top_k or settings.top_k
        logger.info(f"收到问题: {question[:80]}")

        hits = self.vector_store.query(question, top_k=_top_k)
        prompt = format_qa_prompt(question, hits)
        answer = self.llm.generate(prompt, system_prompt=SYSTEM_PROMPT)

        sources = self._extract_sources(hits)

        logger.info(f"回答生成完成，长度: {len(answer)}，引用 {len(sources)} 个来源")
        return QueryResponse(answer=answer, sources=sources, question=question)

    async def aquery(self, question: str, top_k: int | None = None) -> QueryResponse:
        """异步版本的 RAG 问答"""
        _top_k = top_k or settings.top_k
        logger.info(f"收到异步问题: {question[:80]}")

        hits = self.vector_store.query(question, top_k=_top_k)
        prompt = format_qa_prompt(question, hits)
        answer = await self.llm.agenerate(prompt, system_prompt=SYSTEM_PROMPT)

        sources = self._extract_sources(hits)
        return QueryResponse(answer=answer, sources=sources, question=question)

    @staticmethod
    def _extract_sources(hits: list[dict]) -> list[SourceInfo]:
        return [
            SourceInfo(
                filename=hit["metadata"].get("filename", "未知"),
                category=hit["metadata"].get("category", ""),
                score=hit.get("score", 0.0),
                section=hit["metadata"].get("h2", hit["metadata"].get("h1", "")),
            )
            for hit in hits
        ]
