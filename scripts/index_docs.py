"""文档全量索引脚本：首次运行或需要重建时使用"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from loguru import logger
from src.core.rag_pipeline import RAGPipeline
from src.core.vector_store import VectorStore
from src.core.doc_sync import DocumentSyncer, CHECKSUM_FILE


def main():
    logger.info("=" * 50)
    logger.info("知识库文档全量索引")
    logger.info("=" * 50)

    vector_store = VectorStore()
    pipeline = RAGPipeline(vector_store=vector_store)
    count = pipeline.index_all()

    syncer = DocumentSyncer(vector_store=vector_store)
    checksums = syncer.loader.get_file_checksums()
    syncer._save_checksums(checksums)

    logger.info(f"索引完成! 共 {count} 个 chunk 已入库")
    logger.info(f"向量库当前总量: {vector_store.count}")
    logger.info(f"校验和已保存（{len(checksums)} 个文件），后续可增量同步")

    vector_store.close()
    pipeline.llm.close()


if __name__ == "__main__":
    main()
