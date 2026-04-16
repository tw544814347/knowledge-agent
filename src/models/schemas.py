"""Pydantic 数据模型"""

from datetime import datetime
from pydantic import BaseModel, Field
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


class ConversationListResponse(BaseModel):
    """对话列表响应"""
    conversations: List[Conversation] = Field(..., description="对话列表")
    total: int = Field(..., description="总数")


class CreateConversationRequest(BaseModel):
    """创建对话请求"""
    question: str = Field(..., min_length=1, description="用户问题")
    answer: str = Field(..., description="AI回答")
    sources: List[SourceInfo] = Field(default_factory=list, description="参考来源")


class UpdateConversationRequest(BaseModel):
    """更新对话请求"""
    pinned: Optional[bool] = Field(None, description="是否置顶")
