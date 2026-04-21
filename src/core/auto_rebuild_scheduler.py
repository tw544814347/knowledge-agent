"""本地时间夜间窗口内自动全量重建向量索引（每个日历日最多成功一次）"""

from __future__ import annotations

import json
import threading
import time
from datetime import datetime
from pathlib import Path

from loguru import logger

from config.settings import settings
from src.core.doc_sync import DocumentSyncer
from src.core.rag_pipeline import RAGPipeline


class AutoRebuildScheduler:
    """
    在 auto_rebuild_hour_start <= 本地小时 < auto_rebuild_hour_end 时触发 index_all。
    成功后将当日日期写入状态文件；同一自然日已成功过则跳过。
    """

    def __init__(self, pipeline: RAGPipeline, syncer: DocumentSyncer):
        self._pipeline = pipeline
        self._syncer = syncer
        self._lock = threading.Lock()
        self._running = False
        self._thread: threading.Thread | None = None

    def _state_path(self) -> Path:
        p = Path(settings.auto_rebuild_state_file)
        p.parent.mkdir(parents=True, exist_ok=True)
        return p

    def _load_last_success_date(self) -> str | None:
        path = self._state_path()
        if not path.is_file():
            return None
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            return data.get("last_success_date")
        except (json.JSONDecodeError, OSError) as e:
            logger.warning(f"读取自动重建状态失败: {e}")
            return None

    def _save_last_success_date(self, date_str: str) -> None:
        path = self._state_path()
        path.write_text(
            json.dumps({"last_success_date": date_str}, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def _in_night_window(self, now: datetime) -> bool:
        return (
            settings.auto_rebuild_hour_start
            <= now.hour
            < settings.auto_rebuild_hour_end
        )

    def _loop(self) -> None:
        interval = settings.auto_rebuild_check_interval_seconds
        while self._running:
            try:
                if settings.auto_rebuild_enabled:
                    now = datetime.now()
                    today = now.date().isoformat()
                    if self._in_night_window(now):
                        last = self._load_last_success_date()
                        if last == today:
                            pass  # 本日已成功重建过
                        elif self._lock.acquire(blocking=False):
                            try:
                                logger.info(
                                    f"夜间自动全量重建开始 | 本地时间 {now.isoformat(timespec='seconds')}"
                                )
                                count = self._pipeline.index_all()
                                self._syncer.align_checksums_with_disk()
                                self._save_last_success_date(today)
                                logger.info(
                                    f"夜间自动全量重建完成 | chunks={count} | 已记录日期 {today}"
                                )
                            except Exception as e:
                                logger.error(f"夜间自动全量重建失败: {e}")
                            finally:
                                self._lock.release()
            except Exception as e:
                logger.error(f"夜间自动重建调度异常: {e}")

            # 分段 sleep，便于尽快响应 stop
            step = min(1.0, float(interval))
            remaining = float(interval)
            while remaining > 0 and self._running:
                time.sleep(step if remaining >= step else remaining)
                remaining -= step

    def start(self) -> None:
        if not settings.auto_rebuild_enabled:
            logger.info("夜间自动全量重建未启用（AUTO_REBUILD_ENABLED=false）")
            return
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._loop, name="auto-rebuild", daemon=True)
        self._thread.start()
        logger.info(
            f"夜间自动全量重建调度已启动 | 检查间隔 {settings.auto_rebuild_check_interval_seconds}s | "
            f"时间窗 本地 {settings.auto_rebuild_hour_start}:00–{settings.auto_rebuild_hour_end}:00 "
            f"（含起点小时，不含终点小时）"
        )

    def stop(self) -> None:
        self._running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=5.0)
        self._thread = None
        logger.info("夜间自动全量重建调度已停止")
