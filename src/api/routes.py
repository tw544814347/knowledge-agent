"""API 路由定义"""

import json

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.responses import StreamingResponse
from loguru import logger

from src.core.rag_pipeline import RAGPipeline
from src.core.llm_client import LLMError
from src.core.doc_sync import DocumentSyncer
from src.core.conversation_manager import ConversationManager
from src.core.user_manager import UserManager
from src.core.auth_deps import get_current_user, get_current_user_optional, get_user_manager
from src.models.schemas import (
    QueryRequest,
    QueryResponse,
    IndexStatusResponse,
    SyncResponse,
    Conversation,
    ConversationListResponse,
    CreateConversationRequest,
    UpdateConversationRequest,
    UserCreate,
    UserLogin,
    Token,
    User,
    NewChatRequest,
    AskResponseRequest,
    KnowledgeBase,
    KnowledgeBaseListResponse,
    SwitchKnowledgeBaseRequest,
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


# 用户认证相关 API
@router.post("/auth/register", response_model=Token)
async def register(user_create: UserCreate):
    """用户注册"""
    user_manager = get_user_manager()
    try:
        user = user_manager.create_user(user_create)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="邮箱已被注册"
            )
        
        # 创建访问令牌
        user_in_db = user_manager.get_user_by_email(user.email)
        access_token = user_manager.create_access_token(user_in_db)
        
        return Token(access_token=access_token, user=user)
    except Exception as e:
        logger.error(f"用户注册失败: {e}")
        raise HTTPException(status_code=500, detail=f"注册失败: {str(e)}")


@router.post("/auth/login", response_model=Token)
async def login(user_login: UserLogin):
    """用户登录"""
    user_manager = get_user_manager()
    try:
        user_in_db = user_manager.authenticate_user(user_login.email, user_login.password)
        if not user_in_db:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="邮箱或密码错误"
            )
        
        # 创建访问令牌
        access_token = user_manager.create_access_token(user_in_db)
        
        # 转换为User对象（不包含密码）
        user = User(
            id=user_in_db.id,
            email=user_in_db.email,
            nickname=user_in_db.nickname,
            created_at=user_in_db.created_at,
            is_active=user_in_db.is_active
        )
        
        return Token(access_token=access_token, user=user)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"用户登录失败: {e}")
        raise HTTPException(status_code=500, detail=f"登录失败: {str(e)}")


@router.get("/auth/me", response_model=User)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """获取当前用户信息"""
    return current_user


@router.post("/chat/new")
async def new_chat(request: NewChatRequest, current_user: User = Depends(get_current_user)):
    """创建新对话"""
    return {"message": "新对话已创建", "user_id": current_user.id, "clear_current": request.clear_current}


# 对话历史相关 API
@router.post("/conversations", response_model=Conversation)
async def create_conversation(req: CreateConversationRequest, current_user: User = Depends(get_current_user)):
    """保存对话到历史记录"""
    conv_manager = _require_conv_manager()
    try:
        conversation = conv_manager.create_conversation(
            question=req.question,
            answer=req.answer,
            user_id=current_user.id,
            sources=req.sources
        )
        return conversation
    except Exception as e:
        logger.error(f"保存对话失败: {e}")
        raise HTTPException(status_code=500, detail=f"保存对话失败: {str(e)}")


@router.get("/conversations", response_model=ConversationListResponse)
async def get_conversations(limit: int = 10, current_user: User = Depends(get_current_user)):
    """获取历史对话列表"""
    conv_manager = _require_conv_manager()
    try:
        conversations = conv_manager.get_conversations(current_user.id, limit=min(limit, 10))  # 最多10条
        return ConversationListResponse(
            conversations=conversations,
            total=conv_manager.get_conversation_count(current_user.id)
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
async def delete_conversation(conversation_id: str, current_user: User = Depends(get_current_user)):
    """删除对话"""
    conv_manager = _require_conv_manager()
    success = conv_manager.delete_conversation(conversation_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="对话不存在或无权限")
    return {"message": "删除成功"}


@router.post("/chat/new")
async def new_chat(
    request: NewChatRequest,
    current_user: User = Depends(get_current_user)
) -> dict:
    """创建新对话"""
    return {"status": "success", "message": "新对话已创建"}


@router.post("/ask/response")
async def ask_response(request: AskResponseRequest) -> dict:
    """处理ask.py工具的用户响应"""
    logger.info(f"Ask.py response: {request.question} -> {request.selected_option} (index: {request.option_index})")
    return {
        "status": "success", 
        "message": f"已接收用户选择: {request.selected_option}",
        "data": {
            "question": request.question,
            "selected_option": request.selected_option,
            "option_index": request.option_index
        }
    }


@router.get("/ask/check")
async def check_ask_requests() -> dict:
    """检查是否有待处理的ask请求（用于前端轮询）"""
    # 这里可以实现检查ask.py队列的逻辑
    # 暂时返回无请求
    return {
        "has_request": False,
        "request": None
    }


@router.get("/knowledge-bases")
async def get_knowledge_bases(current_user: User = Depends(get_current_user)) -> KnowledgeBaseListResponse:
    """获取可用的知识库列表"""
    # 硬编码几个知识库作为示例，后续可以从配置文件读取
    knowledge_bases = [
        KnowledgeBase(
            id="agent-kb-v1.2",
            name="Agent KB v1.2",
            path="./agent kb v1.2",
            description="主要的AI Agent知识库",
            is_active=True
        ),
        KnowledgeBase(
            id="general-kb",
            name="通用知识库",
            path="./general",
            description="通用技术文档库",
            is_active=True
        ),
        KnowledgeBase(
            id="project-docs",
            name="项目文档",
            path="./project-docs",
            description="项目相关文档",
            is_active=False  # 示例：未激活
        )
    ]
    
    # 当前活跃的知识库（可以从用户配置或全局配置读取）
    current_kb = "agent-kb-v1.2"
    
    return KnowledgeBaseListResponse(
        knowledge_bases=knowledge_bases,
        current=current_kb
    )


@router.post("/knowledge-bases/switch")
async def switch_knowledge_base(
    request: SwitchKnowledgeBaseRequest,
    current_user: User = Depends(get_current_user)
) -> dict:
    """切换知识库"""
    # TODO: 实现知识库切换逻辑
    # 1. 验证知识库ID是否有效
    # 2. 更新用户配置或全局配置
    # 3. 可能需要重新加载向量数据库
    
    logger.info(f"用户 {current_user.email} 请求切换到知识库: {request.kb_id}")
    
    return {
        "status": "success",
        "message": f"已切换到知识库: {request.kb_id}",
        "kb_id": request.kb_id
    }
