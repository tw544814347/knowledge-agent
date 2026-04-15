"""文档处理器：双层 Chunk 策略（Parent Document Retrieval）

小 chunk（~256 字符）用于向量检索 —— 关键词集中，匹配更精准
大 chunk（~1536 字符）用于返回给 LLM —— 上下文完整，回答质量更高

每个小 chunk 的 metadata 中记录其所属大 chunk 的 ID（parent_id），
检索命中后，通过 parent_id 查找完整上下文。
"""

import hashlib

from langchain_text_splitters import (
    MarkdownHeaderTextSplitter,
    RecursiveCharacterTextSplitter,
)
from loguru import logger

from src.core.document_loader import Document
from config.settings import settings

SEPARATORS = ["\n\n", "\n", "。", "；", "，", " ", ""]


class DocumentProcessor:
    """Markdown 文档切分器：两阶段标题切分 + 双层 chunk 生成"""

    MARKDOWN_HEADERS = [
        ("#", "h1"),
        ("##", "h2"),
        ("###", "h3"),
    ]

    def __init__(
        self,
        child_chunk_size: int = settings.chunk_size,
        child_chunk_overlap: int = settings.chunk_overlap,
        parent_chunk_size: int = settings.parent_chunk_size,
        parent_chunk_overlap: int = settings.parent_chunk_overlap,
    ):
        self.header_splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=self.MARKDOWN_HEADERS,
            strip_headers=False,
        )
        self.parent_splitter = RecursiveCharacterTextSplitter(
            chunk_size=parent_chunk_size,
            chunk_overlap=parent_chunk_overlap,
            separators=SEPARATORS,
        )
        self.child_splitter = RecursiveCharacterTextSplitter(
            chunk_size=child_chunk_size,
            chunk_overlap=child_chunk_overlap,
            separators=SEPARATORS,
        )

    def process_documents(
        self, documents: list[Document]
    ) -> tuple[list[Document], dict[str, Document]]:
        """
        批量处理文档。

        @returns: (child_chunks, parent_map)
            - child_chunks: 小 chunk 列表，每个带 parent_id
            - parent_map: {parent_id: 大 chunk Document}
        """
        all_children: list[Document] = []
        parent_map: dict[str, Document] = {}

        for doc in documents:
            children, parents = self._process_single(doc)
            all_children.extend(children)
            parent_map.update(parents)

        logger.info(
            f"共 {len(documents)} 个文档 → "
            f"{len(all_children)} 个检索 chunk + "
            f"{len(parent_map)} 个上下文 chunk"
        )
        return all_children, parent_map

    def _process_single(
        self, doc: Document
    ) -> tuple[list[Document], dict[str, Document]]:
        """对单个文档：先按标题分段，再生成大 chunk 和小 chunk"""
        header_docs = self.header_splitter.split_text(doc.content)
        all_children: list[Document] = []
        parent_map: dict[str, Document] = {}

        for i, header_doc in enumerate(header_docs):
            text = header_doc.page_content
            section_meta = header_doc.metadata

            parent_texts = self.parent_splitter.split_text(text)

            for pi, parent_text in enumerate(parent_texts):
                parent_id = self._make_id(doc.doc_id, i, pi)
                parent_meta = {
                    **doc.metadata,
                    **section_meta,
                    "parent_id": parent_id,
                    "chunk_type": "parent",
                }
                parent_map[parent_id] = Document(
                    content=parent_text, metadata=parent_meta
                )

                child_texts = self.child_splitter.split_text(parent_text)
                for ci, child_text in enumerate(child_texts):
                    child_meta = {
                        **doc.metadata,
                        **section_meta,
                        "parent_id": parent_id,
                        "chunk_type": "child",
                        "chunk_index": len(all_children),
                        "section_index": i,
                        "sub_index": ci,
                    }
                    all_children.append(
                        Document(content=child_text, metadata=child_meta)
                    )

        if not all_children:
            parent_texts = self.parent_splitter.split_text(doc.content)
            for pi, parent_text in enumerate(parent_texts):
                parent_id = self._make_id(doc.doc_id, 0, pi)
                parent_map[parent_id] = Document(
                    content=parent_text,
                    metadata={**doc.metadata, "parent_id": parent_id, "chunk_type": "parent"},
                )
                child_texts = self.child_splitter.split_text(parent_text)
                for ci, child_text in enumerate(child_texts):
                    child_meta = {
                        **doc.metadata,
                        "parent_id": parent_id,
                        "chunk_type": "child",
                        "chunk_index": len(all_children),
                        "sub_index": ci,
                    }
                    all_children.append(
                        Document(content=child_text, metadata=child_meta)
                    )

        return all_children, parent_map

    @staticmethod
    def _make_id(doc_id: str, section: int, part: int) -> str:
        raw = f"{doc_id}_s{section}_p{part}"
        return hashlib.md5(raw.encode()).hexdigest()[:16]
