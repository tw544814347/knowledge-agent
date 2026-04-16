"""Pydantic 数据模型"""

from datetime import datetime
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional


class QueryRequest(BaseModel):
    """问答请求"""
    question: str = Field(..., min_length=1, description="用户问题")
    top_k: int = Field(default=5, ge=1, le=20, description="检索文档数量")


class SourceInfo(BaseModel):
    """引用来源信息"""
    filename: str
    category: str = ""
    score: float = 0.0
    section: str = ""
    related_docs: list[str] = Field(default_factory=list, description="关联文档列表")


class QueryResponse(BaseModel):
    """问答响应"""
    answer: str = Field(..., description="AI 生成的回答")
    sources: list[SourceInfo] = Field(default_factory=list, description="参考来源")
    question: str = Field(..., description="原始问题")


class IndexStatusResponse(BaseModel):
    """索引状态"""
    total_chunks: int = Field(..., description="向量库中的 chunk 总数")
    source_dir: str = Field(..., description="知识文档源目录")
    last_sync: str | None = Field(None, description="最近同步时间")


class SyncResponse(BaseModel):
    """同步结果"""
    added: int = 0
    updated: int = 0
    deleted: int = 0
    total_chunks: int = 0
    message: str = ""


# 历史对话相关模型
class ConversationMessage(BaseModel):
    """对话消息"""
    question: str = Field(..., description="用户问题")
    answer: str = Field(..., description="AI回答")
    sources: List[SourceInfo] = Field(default_factory=list, description="参考来源")


class Conversation(BaseModel):
    """对话记录"""
    id: str = Field(..., description="对话ID")
    title: str = Field(..., description="对话标题（从问题自动生成）")
    message: ConversationMessage = Field(..., description="对话内容")
    created_at: datetime = Field(..., description="创建时间")
    pinned: bool = Field(default=False, description="是否置顶")
    user_id: str = Field(..., description="所属用户ID")


class ConversationListResponse(BaseModel):
    """对话列表响应"""
    conversations: List[Conversation] = Field(..., description="对话列表")
    total: int = Field(..., description="总数")


class CreateConversationRequest(BaseModel):
    """创建对话请求"""
    question: str = Field(..., min_length=1, description="用户问题")
    answer: str = Field(..., description="AI回答")
    sources: List[SourceInfo] = Field(default_factory=list, description="参考来源")


class NewChatRequest(BaseModel):
    """新对话请求"""
    clear_current: bool = Field(default=True, description="是否清空当前对话")


class AskResponseRequest(BaseModel):
    """ask.py工具响应请求"""
    question: str = Field(..., description="问题内容")
    selected_option: str = Field(..., description="用户选择的选项")
    option_index: int = Field(..., description="选项索引")


class UpdateConversationRequest(BaseModel):
    """更新对话请求"""
    pinned: Optional[bool] = Field(None, description="是否置顶")


# 用户认证相关模型
class UserCreate(BaseModel):
    """用户注册请求"""
    email: EmailStr = Field(..., description="邮箱地址")
    password: str = Field(..., min_length=6, description="密码（至少6位）")
    nickname: Optional[str] = Field(None, max_length=50, description="昵称")


class UserLogin(BaseModel):
    """用户登录请求"""
    email: EmailStr = Field(..., description="邮箱地址")
    password: str = Field(..., description="密码")


class User(BaseModel):
    """用户信息"""
    id: str = Field(..., description="用户ID")
    email: str = Field(..., description="邮箱地址")
    nickname: Optional[str] = Field(None, description="昵称")
    created_at: datetime = Field(..., description="创建时间")
    is_active: bool = Field(default=True, description="是否激活")


class UserInDB(User):
    """数据库中的用户信息（包含密码哈希）"""
    hashed_password: str = Field(..., description="密码哈希")


class Token(BaseModel):
    """JWT Token响应"""
    access_token: str = Field(..., description="访问令牌")
    token_type: str = Field(default="bearer", description="令牌类型")
    user: User = Field(..., description="用户信息")


class TokenData(BaseModel):
    """Token载荷数据"""
    user_id: Optional[str] = None
    email: Optional[str] = None
