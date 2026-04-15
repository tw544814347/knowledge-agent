"""Pydantic 数据模型"""

from pydantic import BaseModel, Field


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
