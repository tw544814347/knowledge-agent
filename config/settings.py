"""项目配置：从 .env 加载，所有模块共用"""

from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    # Ollama
    ollama_base_url: str = Field(default="http://localhost:11434", alias="OLLAMA_BASE_URL")
    llm_model: str = Field(default="deepseek-r1:14b", alias="LLM_MODEL")
    embedding_model: str = Field(default="bge-m3", alias="EMBEDDING_MODEL")

    # LLM 参数
    llm_temperature: float = Field(default=0.2, alias="LLM_TEMPERATURE")
    llm_top_p: float = Field(default=0.9, alias="LLM_TOP_P")
    llm_max_tokens: int = Field(default=2048, alias="LLM_MAX_TOKENS")

    # RAG — 小 chunk 用于检索，大 chunk 用于上下文返回（Parent Document Retrieval）
    chunk_size: int = Field(default=256, alias="CHUNK_SIZE")
    chunk_overlap: int = Field(default=32, alias="CHUNK_OVERLAP")
    parent_chunk_size: int = Field(default=1536, alias="PARENT_CHUNK_SIZE")
    parent_chunk_overlap: int = Field(default=128, alias="PARENT_CHUNK_OVERLAP")
    top_k: int = Field(default=8, alias="TOP_K")
    min_score: float = Field(default=0.5, alias="MIN_SCORE")
    max_chunks_per_doc: int = Field(default=3, alias="MAX_CHUNKS_PER_DOC")

    # ChromaDB
    chroma_persist_dir: str = Field(default="./data/vectordb", alias="CHROMA_PERSIST_DIR")
    chroma_collection_name: str = Field(default="knowledge_base", alias="CHROMA_COLLECTION_NAME")

    # 知识文档
    knowledge_source_dir: str = Field(
        default="./knowledge",
        alias="KNOWLEDGE_SOURCE_DIR",
    )

    # 文档同步
    sync_interval: int = Field(default=300, alias="SYNC_INTERVAL")

    # API
    api_host: str = Field(default="0.0.0.0", alias="API_HOST")
    api_port: int = Field(default=8000, alias="API_PORT")

    # 日志
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        populate_by_name = True


settings = Settings()
