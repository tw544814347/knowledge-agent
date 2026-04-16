"""API 路由定义"""

import json

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from loguru import logger

from src.core.rag_pipeline import RAGPipeline
from src.core.llm_client import LLMError
from src.core.doc_sync import DocumentSyncer
from src.core.conversation_manager import ConversationManager
from src.models.schemas import (
    QueryRequest,
    QueryResponse,
    IndexStatusResponse,
    SyncResponse,
    Conversation,
    ConversationListResponse,
    CreateConversationRequest,
    UpdateConversationRequest,
)
from config.settings import settings

router = APIRouter()

_pipeline: RAGPipeline | None = None
_syncer: DocumentSyncer | None = None
_conv_manager: ConversationManager | None = None


def set_dependencies(pipeline: RAGPipeline, syncer: DocumentSyncer, conv_manager: ConversationManager) -> None:
    """由 main.py lifespan 注入共享的 pipeline、syncer 和 conversation_manager 实例"""
    global _pipeline, _syncer, _conv_manager
    _pipeline = pipeline
    _syncer = syncer
    _conv_manager = conv_manager


def _require_pipeline() -> RAGPipeline:
    if _pipeline is None:
        raise HTTPException(status_code=503, detail="服务尚未初始化")
    return _pipeline


def _require_syncer() -> DocumentSyncer:
    if _syncer is None:
        raise HTTPException(status_code=503, detail="服务尚未初始化")
    return _syncer


def _require_conv_manager() -> ConversationManager:
    if _conv_manager is None:
        raise HTTPException(status_code=503, detail="服务尚未初始化")
    return _conv_manager


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


@router.post("/ask/stream")
async def ask_question_stream(req: QueryRequest):
    """流式知识库问答：先返回检索来源，再逐 token 返回回答"""
    pipeline = _require_pipeline()

    def generate():
        try:
            for chunk in pipeline.stream_query(req.question, top_k=req.top_k):
                yield json.dumps(chunk, ensure_ascii=False) + "\n"
        except Exception as e:
            logger.error(f"流式问答失败: {e}")
            yield json.dumps({"type": "error", "message": str(e)}, ensure_ascii=False) + "\n"

    return StreamingResponse(generate(), media_type="text/plain; charset=utf-8")


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


# 对话历史相关 API
@router.post("/conversations", response_model=Conversation)
async def create_conversation(req: CreateConversationRequest):
    """保存对话到历史记录"""
    conv_manager = _require_conv_manager()
    try:
        conversation = conv_manager.create_conversation(
            question=req.question,
            answer=req.answer,
            sources=req.sources
        )
        return conversation
    except Exception as e:
        logger.error(f"保存对话失败: {e}")
        raise HTTPException(status_code=500, detail=f"保存对话失败: {str(e)}")


@router.get("/conversations", response_model=ConversationListResponse)
async def get_conversations(limit: int = 20):
    """获取历史对话列表"""
    conv_manager = _require_conv_manager()
    try:
        conversations = conv_manager.get_conversations(limit=min(limit, 50))  # 最多50条
        return ConversationListResponse(
            conversations=conversations,
            total=conv_manager.get_conversation_count()
        )
    except Exception as e:
        logger.error(f"获取对话列表失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取对话列表失败: {str(e)}")


@router.get("/conversations/{conversation_id}", response_model=Conversation)
async def get_conversation(conversation_id: str):
    """根据ID获取对话详情"""
    conv_manager = _require_conv_manager()
    conversation = conv_manager.get_conversation(conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="对话不存在")
    return conversation


@router.put("/conversations/{conversation_id}", response_model=Conversation)
async def update_conversation(conversation_id: str, req: UpdateConversationRequest):
    """更新对话（如置顶/取消置顶）"""
    conv_manager = _require_conv_manager()
    conversation = conv_manager.update_conversation(
        conversation_id=conversation_id,
        pinned=req.pinned
    )
    if not conversation:
        raise HTTPException(status_code=404, detail="对话不存在")
    return conversation


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str):
    """删除对话"""
    conv_manager = _require_conv_manager()
    success = conv_manager.delete_conversation(conversation_id)
    if not success:
        raise HTTPException(status_code=404, detail="对话不存在")
    return {"message": "删除成功"}
