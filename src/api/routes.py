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
from src.core.knowledge_base_manager import KnowledgeBaseManager
from src.core.email_service import EmailService
from src.core.auth_deps import get_current_user, get_current_user_optional, get_user_manager
from src.models.schemas import (
    QueryRequest,
    QueryResponse,
    IndexStatusResponse,
    SyncResponse,
    Conversation,
    ConversationListResponse,
    CreateConversationRequest,
    MessageLikeRequest,
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
    ForgotPasswordRequest,
    ResetPasswordRequest,
    ChangePasswordRequest,
    SendRegistrationCodeRequest,
    VerifyRegistrationRequest,
)
from config.settings import settings

router = APIRouter()

_pipeline: RAGPipeline | None = None
_syncer: DocumentSyncer | None = None
_conv_manager: ConversationManager | None = None
_user_manager: UserManager | None = None
_kb_manager: KnowledgeBaseManager | None = None
_email_service: EmailService | None = None


def set_dependencies(pipeline: RAGPipeline, syncer: DocumentSyncer, conv_manager: ConversationManager, user_manager: UserManager, kb_manager: KnowledgeBaseManager, email_service: EmailService) -> None:
    """由 main.py lifespan 注入共享的实例"""
    global _pipeline, _syncer, _conv_manager, _user_manager, _kb_manager, _email_service
    _pipeline = pipeline
    _syncer = syncer
    _conv_manager = conv_manager
    _user_manager = user_manager
    _kb_manager = kb_manager
    _email_service = email_service


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


def _require_user_manager() -> UserManager:
    if _user_manager is None:
        raise HTTPException(status_code=503, detail="服务尚未初始化")
    return _user_manager


def _require_kb_manager() -> KnowledgeBaseManager:
    if _kb_manager is None:
        raise HTTPException(status_code=503, detail="服务尚未初始化")
    return _kb_manager


def _require_email_service() -> EmailService:
    if _email_service is None:
        raise HTTPException(status_code=503, detail="邮件服务尚未初始化")
    return _email_service


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
async def ask_question_stream(
    req: QueryRequest, 
    current_user: User = Depends(get_current_user)
):
    """流式知识库问答：先返回检索来源，再逐 token 返回回答，并自动保存到历史记录"""
    pipeline = _require_pipeline()
    conv_manager = _require_conv_manager()
    
    # 用于收集完整的回答内容
    full_answer = []
    sources = []

    def generate():
        nonlocal full_answer, sources
        try:
            for chunk in pipeline.stream_query(req.question, top_k=req.top_k):
                # 收集sources信息
                if chunk.get("type") == "sources":
                    sources = chunk.get("sources", [])
                
                # 收集答案token
                if chunk.get("type") == "token":
                    token = chunk.get("content", "")
                    full_answer.append(token)
                
                # 流式输出给前端
                yield json.dumps(chunk, ensure_ascii=False) + "\n"
                
                # 如果是完成信号，保存对话到历史记录
                if chunk.get("type") == "done":
                    try:
                        complete_answer = "".join(full_answer)
                        if complete_answer.strip():  # 只有非空回答才保存
                            # 自动保存对话到历史记录
                            conversation = conv_manager.create_conversation(
                                question=req.question,
                                answer=complete_answer,
                                user_id=current_user.id,
                                sources=sources,
                                conversation_id=req.conversation_id,
                            )
                            logger.info(f"自动保存对话到历史记录: {conversation.id}")
                            idx = len(conversation.messages) - 1
                            yield json.dumps(
                                {
                                    "type": "conversation_saved",
                                    "conversation_id": conversation.id,
                                    "message_index": max(0, idx),
                                },
                                ensure_ascii=False,
                            ) + "\n"
                    except Exception as save_error:
                        logger.error(f"保存对话到历史记录失败: {save_error}")
                        # 不影响流式响应，静默失败
                        
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
        syncer.align_checksums_with_disk()
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
    email_service = _require_email_service()
    
    try:
        user = user_manager.create_user(user_create)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="邮箱已被注册"
            )
        
        # 发送欢迎邮件
        try:
            email_service.send_welcome_email(user.email, user.nickname or "用户")
            logger.info(f"欢迎邮件已发送到: {user.email}")
        except Exception as email_error:
            logger.error(f"发送欢迎邮件失败: {email_error}")
            # 邮件发送失败不影响注册流程
        
        # 创建访问令牌
        user_in_db = user_manager.get_user_by_email(user.email)
        access_token = user_manager.create_access_token(user_in_db)
        
        return Token(access_token=access_token, user=user)
    except HTTPException:
        raise
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
async def get_conversation(conversation_id: str, current_user: User = Depends(get_current_user)):
    """根据ID获取对话详情"""
    conv_manager = _require_conv_manager()
    conversation = conv_manager.get_conversation(conversation_id, current_user.id)
    if not conversation:
        raise HTTPException(status_code=404, detail="对话不存在")
    return conversation


@router.put("/conversations/{conversation_id}", response_model=Conversation)
async def update_conversation(conversation_id: str, req: UpdateConversationRequest, current_user: User = Depends(get_current_user)):
    """更新对话（如置顶/取消置顶）"""
    conv_manager = _require_conv_manager()
    conversation = conv_manager.update_conversation(
        conversation_id=conversation_id,
        user_id=current_user.id,
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


@router.put("/conversations/{conversation_id}/messages/{message_index}/like", response_model=Conversation)
async def set_message_like(
    conversation_id: str,
    message_index: int,
    body: MessageLikeRequest,
    current_user: User = Depends(get_current_user),
):
    """对某条问答点赞或取消；语料写入 agent kb v1.2/liked_answers/ 并触发增量同步"""
    if message_index < 0:
        raise HTTPException(status_code=400, detail="无效的消息索引")
    conv_manager = _require_conv_manager()
    result = conv_manager.set_message_liked(
        conversation_id, current_user.id, message_index, body.liked
    )
    if not result:
        raise HTTPException(status_code=404, detail="对话不存在或消息索引无效")
    syncer = _require_syncer()
    try:
        syncer.sync()
    except Exception as e:
        logger.warning(f"点赞语料入库同步失败（可依赖定时同步）: {e}")
    return result


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
    kb_manager = _require_kb_manager()
    
    knowledge_bases = kb_manager.get_knowledge_bases()
    current_kb = kb_manager.get_current_knowledge_base()
    
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
    kb_manager = _require_kb_manager()
    
    # 验证并设置知识库
    success = kb_manager.set_current_knowledge_base(request.kb_id)
    
    if not success:
        raise HTTPException(
            status_code=400, 
            detail=f"无法切换到知识库 {request.kb_id}，请确认知识库存在且可用"
        )
    
    logger.info(f"用户 {current_user.email} 成功切换到知识库: {request.kb_id}")
    
    # TODO: 在这里可以实现向量库的热重载
    # 目前只是记录切换，实际的向量库切换需要重启服务
    
    return {
        "status": "success",
        "message": f"已切换到知识库: {request.kb_id}",
        "kb_id": request.kb_id,
        "note": "知识库切换已保存，向量库将在下次重启时生效"
    }


@router.post("/auth/forgot-password")
async def forgot_password(request: ForgotPasswordRequest) -> dict:
    """忘记密码 - 发送重置验证码"""
    user_manager = _require_user_manager()
    email_service = _require_email_service()
    
    # 生成重置验证码
    reset_code = user_manager.generate_reset_code(request.email)
    
    if not reset_code:
        # 为了安全，即使用户不存在也返回成功消息
        return {
            "status": "success",
            "message": "如果该邮箱存在，您将收到密码重置邮件"
        }
    
    # 发送邮件
    email_sent = email_service.send_password_reset_email(request.email, reset_code)
    
    if email_sent:
        logger.info(f"密码重置邮件已发送到: {request.email}")
        return {
            "status": "success",
            "message": "密码重置邮件已发送，请查收您的邮箱"
        }
    else:
        logger.error(f"发送密码重置邮件失败: {request.email}")
        raise HTTPException(
            status_code=500, 
            detail="邮件发送失败，请稍后重试"
        )


@router.post("/auth/reset-password")
async def reset_password(request: ResetPasswordRequest) -> dict:
    """重置密码"""
    user_manager = _require_user_manager()
    
    # 重置密码
    success = user_manager.reset_password(
        request.email, 
        request.reset_code, 
        request.new_password
    )
    
    if not success:
        raise HTTPException(
            status_code=400, 
            detail="验证码无效或已过期，请重新申请密码重置"
        )
    
    logger.info(f"用户 {request.email} 密码重置成功")
    return {
        "status": "success",
        "message": "密码重置成功，请使用新密码登录"
    }

@router.post("/auth/change-password")
async def change_password(
    request: ChangePasswordRequest,
    current_user: User = Depends(get_current_user)
) -> dict:
    """修改密码（需要登录）"""
    user_manager = _require_user_manager()
    
    # 验证当前密码
    user_in_db = user_manager.get_user_by_email(current_user.email)
    if not user_in_db or not user_manager.verify_password(request.current_password, user_in_db.hashed_password):
        raise HTTPException(status_code=400, detail="当前密码不正确")
    
    # 更新密码
    try:
        # 直接修改用户管理器中的用户数据
        if current_user.id in user_manager._users:
            user_manager._users[current_user.id]['hashed_password'] = user_manager.get_password_hash(request.new_password)
            user_manager._save_users()  # 保存到文件
        else:
            raise HTTPException(status_code=404, detail="用户不存在")
    except Exception as e:
        logger.error(f"密码修改失败: {e}")
        raise HTTPException(status_code=500, detail="密码修改失败")
    
    logger.info(f"用户 {current_user.email} 密码修改成功")
    return {
        "status": "success",
        "message": "密码修改成功"
    }

@router.post("/auth/send-registration-code")
async def send_registration_code(request: SendRegistrationCodeRequest) -> dict:
    """发送注册验证码"""
    user_manager = _require_user_manager()
    email_service = _require_email_service()
    
    try:
        # 生成验证码
        verification_code = user_manager.generate_registration_code(request.email)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    # 发送验证邮件
    if email_service.send_registration_verification_email(request.email, verification_code):
        logger.info(f"注册验证码已发送到: {request.email}")
        return {
            "status": "success",
            "message": "验证码已发送到您的邮箱，请查收"
        }
    else:
        logger.error(f"发送注册验证码失败: {request.email}")
        raise HTTPException(
            status_code=500, 
            detail="验证码发送失败，请稍后重试"
        )

@router.post("/auth/verify-registration", response_model=Token)
async def verify_registration(request: VerifyRegistrationRequest):
    """验证注册（使用验证码）"""
    user_manager = _require_user_manager()
    email_service = _require_email_service()
    
    # 验证验证码
    if not user_manager.verify_registration_code(request.email, request.verification_code):
        raise HTTPException(
            status_code=400, 
            detail="验证码无效或已过期，请重新获取验证码"
        )
    
    try:
        # 创建用户（不再需要检查邮箱是否已存在，验证码生成时已检查）
        user_create = UserCreate(
            email=request.email,
            password=request.password,
            nickname=request.nickname
        )
        user = user_manager.create_user(user_create)
        
        if not user:
            raise HTTPException(
                status_code=400,
                detail="注册失败，邮箱可能已被注册"
            )
        
        # 发送欢迎邮件（注册成功后发送）
        try:
            email_service.send_welcome_email(user.email, user.nickname or "用户")
            logger.info(f"欢迎邮件已发送到: {user.email}")
        except Exception as email_error:
            logger.error(f"发送欢迎邮件失败: {email_error}")
            # 邮件发送失败不影响注册流程
        
        # 创建访问令牌
        user_in_db = user_manager.get_user_by_email(user.email)
        access_token = user_manager.create_access_token(user_in_db)
        
        return Token(access_token=access_token, user=user)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"验证注册失败: {e}")
        raise HTTPException(status_code=500, detail=f"注册失败: {str(e)}")
