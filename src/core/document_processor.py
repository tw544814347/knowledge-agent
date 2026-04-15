"""文档处理器：将文档切分为适合向量化的 chunk"""

from langchain_text_splitters import (
    MarkdownHeaderTextSplitter,
    RecursiveCharacterTextSplitter,
)
from loguru import logger

from src.core.document_loader import Document
from config.settings import settings


class DocumentProcessor:
    """Markdown 文档切分器，支持按标题层级 + 递归字符切分的两阶段策略"""

    MARKDOWN_HEADERS = [
        ("#", "h1"),
        ("##", "h2"),
        ("###", "h3"),
    ]

    def __init__(
        self,
        chunk_size: int = settings.chunk_size,
        chunk_overlap: int = settings.chunk_overlap,
    ):
        self.header_splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=self.MARKDOWN_HEADERS,
            strip_headers=False,
        )
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", "。", "；", "，", " ", ""],
        )

    def process_documents(self, documents: list[Document]) -> list[Document]:
        """批量处理文档，返回切分后的 chunk 列表"""
        all_chunks: list[Document] = []

        for doc in documents:
            chunks = self._process_single(doc)
            all_chunks.extend(chunks)

        logger.info(f"共 {len(documents)} 个文档 → {len(all_chunks)} 个 chunk")
        return all_chunks

    def _process_single(self, doc: Document) -> list[Document]:
        """两阶段切分：先按 Markdown 标题，再按字符长度"""
        header_docs = self.header_splitter.split_text(doc.content)

        chunks: list[Document] = []
        for i, header_doc in enumerate(header_docs):
            text = header_doc.page_content
            section_meta = header_doc.metadata  # h1, h2, h3 等

            sub_texts = self.text_splitter.split_text(text)

            for j, sub_text in enumerate(sub_texts):
                chunk_meta = {
                    **doc.metadata,
                    **section_meta,
                    "chunk_index": len(chunks),
                    "section_index": i,
                    "sub_index": j,
                }
                chunks.append(Document(content=sub_text, metadata=chunk_meta))

        if not chunks:
            sub_texts = self.text_splitter.split_text(doc.content)
            for j, sub_text in enumerate(sub_texts):
                chunk_meta = {**doc.metadata, "chunk_index": j}
                chunks.append(Document(content=sub_text, metadata=chunk_meta))

        return chunks
