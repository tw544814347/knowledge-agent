"""FastAPI 主入口"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from config.settings import settings
from src.core.vector_store import VectorStore
from src.core.rag_pipeline import RAGPipeline
from src.core.doc_sync import DocumentSyncer
from src.api.routes import router, set_dependencies


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(
        f"知识库 Agent 启动 | LLM: {settings.llm_model} | "
        f"Embedding: {settings.embedding_model}"
    )
    vector_store = VectorStore()
    pipeline = RAGPipeline(vector_store=vector_store)
    syncer = DocumentSyncer(vector_store=vector_store)
    set_dependencies(pipeline, syncer)
    syncer.start_background_sync()
    yield
    syncer.stop_background_sync()
    vector_store.close()
    pipeline.llm.close()
    logger.info("知识库 Agent 关闭")


app = FastAPI(
    title="知识库 Agent API",
    description="基于 DeepSeek R1 的本地知识库智能问答系统",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "model": settings.llm_model,
        "embedding_model": settings.embedding_model,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.api.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True,
    )
