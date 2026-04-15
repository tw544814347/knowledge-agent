"""项目配置：从 .env 加载，所有模块共用"""

from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    # Ollama
    ollama_base_url: str = Field(default="http://localhost:11434", alias="OLLAMA_BASE_URL")
    llm_model: str = Field(default="deepseek-r1:7b", alias="LLM_MODEL")
    embedding_model: str = Field(default="nomic-embed-text", alias="EMBEDDING_MODEL")

    # LLM 参数
    llm_temperature: float = Field(default=0.7, alias="LLM_TEMPERATURE")
    llm_top_p: float = Field(default=0.9, alias="LLM_TOP_P")
    llm_max_tokens: int = Field(default=2048, alias="LLM_MAX_TOKENS")

    # RAG
    chunk_size: int = Field(default=512, alias="CHUNK_SIZE")
    chunk_overlap: int = Field(default=50, alias="CHUNK_OVERLAP")
    top_k: int = Field(default=5, alias="TOP_K")

    # ChromaDB
    chroma_persist_dir: str = Field(default="./data/vectordb", alias="CHROMA_PERSIST_DIR")
    chroma_collection_name: str = Field(default="knowledge_base", alias="CHROMA_COLLECTION_NAME")

    # 知识文档
    knowledge_source_dir: str = Field(
        default="/Users/wei.tao/Desktop/Data Confluence",
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
