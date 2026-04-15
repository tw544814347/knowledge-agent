"""文档同步模块：检测文件变更并增量更新向量库"""

import json
import threading
from pathlib import Path
from datetime import datetime

from loguru import logger

from config.settings import settings
from src.core.document_loader import DocumentLoader
from src.core.document_processor import DocumentProcessor
from src.core.vector_store import VectorStore
from src.models.schemas import SyncResponse

CHECKSUM_FILE = Path(settings.chroma_persist_dir) / ".checksums.json"


class DocumentSyncer:
    """
    增量文档同步器：
    - 比对文件 MD5 校验和，检测新增/修改/删除
    - 仅对变更文件进行重新索引
    - 支持后台定时同步
    """

    def __init__(self, vector_store: VectorStore | None = None):
        self.loader = DocumentLoader(settings.knowledge_source_dir)
        self.processor = DocumentProcessor()
        self.vector_store = vector_store or VectorStore()
        self.last_sync_time: str | None = None
        self._timer: threading.Timer | None = None
        self._running = False

    def _load_saved_checksums(self) -> dict[str, str]:
        if CHECKSUM_FILE.exists():
            return json.loads(CHECKSUM_FILE.read_text(encoding="utf-8"))
        return {}

    def _save_checksums(self, checksums: dict[str, str]) -> None:
        CHECKSUM_FILE.parent.mkdir(parents=True, exist_ok=True)
        CHECKSUM_FILE.write_text(
            json.dumps(checksums, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def sync(self) -> SyncResponse:
        """执行一次增量同步"""
        logger.info("开始文档同步...")

        old_checksums = self._load_saved_checksums()
        new_checksums = self.loader.get_file_checksums()

        old_files = set(old_checksums.keys())
        new_files = set(new_checksums.keys())

        added_files = new_files - old_files
        deleted_files = old_files - new_files
        modified_files = {
            f for f in (old_files & new_files)
            if old_checksums[f] != new_checksums[f]
        }

        changed_files = added_files | modified_files
        added_count = len(added_files)
        updated_count = len(modified_files)
        deleted_count = len(deleted_files)

        for f in deleted_files:
            self.vector_store.delete_by_source(f)
            logger.info(f"已删除: {Path(f).name}")

        if changed_files:
            documents = []
            for f in changed_files:
                doc = self.loader.load_file(f)
                if doc:
                    documents.append(doc)
                else:
                    logger.warning(f"加载变更文件失败: {f}")

            if documents:
                for doc in documents:
                    self.vector_store.delete_by_source(doc.metadata["source"])

                chunks = self.processor.process_documents(documents)
                self.vector_store.add_documents(chunks)
                logger.info(f"已更新 {len(documents)} 个文件 → {len(chunks)} 个 chunk")

        self._save_checksums(new_checksums)
        self.last_sync_time = datetime.now().isoformat()

        total = self.vector_store.count
        msg = f"同步完成: +{added_count} 新增, ~{updated_count} 更新, -{deleted_count} 删除"
        logger.info(msg)

        return SyncResponse(
            added=added_count,
            updated=updated_count,
            deleted=deleted_count,
            total_chunks=total,
            message=msg,
        )

    def start_background_sync(self, interval: int = settings.sync_interval) -> None:
        """启动后台定时同步"""
        if self._running:
            return
        self._running = True
        logger.info(f"后台同步已启动，间隔 {interval} 秒")
        self._schedule(interval)

    def _schedule(self, interval: int) -> None:
        if not self._running:
            return

        def _run():
            try:
                self.sync()
            except Exception as e:
                logger.error(f"后台同步失败: {e}")
            finally:
                self._schedule(interval)

        self._timer = threading.Timer(interval, _run)
        self._timer.daemon = True
        self._timer.start()

    def stop_background_sync(self) -> None:
        """停止后台同步"""
        self._running = False
        if self._timer:
            self._timer.cancel()
        logger.info("后台同步已停止")
