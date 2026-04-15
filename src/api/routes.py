"""API 路由定义"""

from fastapi import APIRouter, HTTPException
from loguru import logger

from src.core.rag_pipeline import RAGPipeline
from src.core.llm_client import LLMError
from src.core.doc_sync import DocumentSyncer
from src.models.schemas import (
    QueryRequest,
    QueryResponse,
    IndexStatusResponse,
    SyncResponse,
)
from config.settings import settings

router = APIRouter()

_pipeline: RAGPipeline | None = None
_syncer: DocumentSyncer | None = None


def set_dependencies(pipeline: RAGPipeline, syncer: DocumentSyncer) -> None:
    """由 main.py lifespan 注入共享的 pipeline 和 syncer 实例"""
    global _pipeline, _syncer
    _pipeline = pipeline
    _syncer = syncer


def _require_pipeline() -> RAGPipeline:
    if _pipeline is None:
        raise HTTPException(status_code=503, detail="服务尚未初始化")
    return _pipeline


def _require_syncer() -> DocumentSyncer:
    if _syncer is None:
        raise HTTPException(status_code=503, detail="服务尚未初始化")
    return _syncer


@router.post("/ask", response_model=QueryResponse)
async def ask_question(req: QueryRequest):
    """知识库问答接口"""
    pipeline = _require_pipeline()
    try:
        result = await pipeline.aquery(req.question, top_k=req.top_k)
        return result
    except LLMError as e:
        raise HTTPException(status_code=502, detail=str(e))
    except Exception as e:
        logger.error(f"问答失败: {e}")
        raise HTTPException(status_code=500, detail=f"问答处理失败: {str(e)}")


@router.post("/sync", response_model=SyncResponse)
async def sync_documents():
    """增量文档同步接口"""
    syncer = _require_syncer()
    try:
        result = syncer.sync()
        return result
    except Exception as e:
        logger.error(f"同步失败: {e}")
        raise HTTPException(status_code=500, detail=f"同步失败: {str(e)}")


@router.post("/rebuild", response_model=IndexStatusResponse)
async def rebuild_index():
    """重建全量索引"""
    pipeline = _require_pipeline()
    syncer = _require_syncer()
    try:
        count = pipeline.index_all()
        return IndexStatusResponse(
            total_chunks=count,
            source_dir=settings.knowledge_source_dir,
            last_sync=syncer.last_sync_time,
        )
    except Exception as e:
        logger.error(f"重建索引失败: {e}")
        raise HTTPException(status_code=500, detail=f"重建失败: {str(e)}")


@router.get("/status", response_model=IndexStatusResponse)
async def get_status():
    """获取索引状态"""
    pipeline = _require_pipeline()
    syncer = _require_syncer()
    return IndexStatusResponse(
        total_chunks=pipeline.vector_store.count,
        source_dir=settings.knowledge_source_dir,
        last_sync=syncer.last_sync_time,
    )
