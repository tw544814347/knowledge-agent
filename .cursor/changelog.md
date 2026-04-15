# 知识库 Agent 变更日志

## 2026-04-15（代码审查与修复）

### Rules 修复

- 技术栈表修正：移除未使用的 FAISS、LlamaIndex，改为实际使用的 langchain-text-splitters、httpx
- 知识文档管理描述改为通过 `.env` 配置外部目录，不再写死 `docs/knowledge/`
- Prompt 工程规范改为 "f-string"，移除未使用的 Jinja2
- 新增"资源管理规范"：单例模式、禁用 `__del__`
- 新增"错误应抛出自定义异常，禁止吞掉异常"

### 严重 Bug 修复

- **document_loader.py**: 移除 PDF/DOCX 虚假支持（`read_text` 无法读二进制文件），只保留 .md/.txt；新增 `load_file()` 方法供增量同步使用
- **doc_sync.py**: 修复 O(N*M) 性能灾难——每个变更文件不再 `load_all()` 全量加载，改为 `load_file()` 只加载单个文件
- **多实例状态不共享**: `main.py` 创建共享的 `VectorStore` 实例，通过依赖注入传给 `RAGPipeline` 和 `DocumentSyncer`；`routes.py` 通过 `set_dependencies()` 接收共享实例
- **index_docs.py**: 修复全量索引后又 `sync()` 导致重复写入；改为只保存校验和，不再触发 sync
- **rag_pipeline.py**: 移除多余的 `@dataclass` 装饰器；提取 `_extract_sources` 复用

### 代码质量改进

- **llm_client.py**: 错误不再被吞掉，改为抛出 `LLMError` 自定义异常；新增 tenacity 重试机制（3 次指数退避）；新增调用耗时日志
- **vector_store.py**: `ChromaEmbeddingFunction.__call__` 参数名从 `input` 改为 `texts`；Embedding 调用新增重试机制；`__del__` 改为显式 `close()` 方法
- **query_cli.py**: 新增 `LLMError` 捕获；退出时清理资源
- **routes.py**: 依赖改为由 lifespan 注入，不再自行创建实例；LLM 错误返回 502 而非 500
- **requirements.txt**: 移除未使用的 `python-dotenv`；新增 `tenacity`

## 2026-04-15（项目初始化）

### 核心模块实现

- `config/settings.py`：基于 pydantic-settings 的配置管理
- `src/core/document_loader.py`：Markdown 文档加载器
- `src/core/document_processor.py`：两阶段文档切分
- `src/core/vector_store.py`：ChromaDB 向量存储 + Ollama Embedding
- `src/core/llm_client.py`：Ollama REST API 客户端
- `src/core/rag_pipeline.py`：完整 RAG 流程编排
- `src/core/doc_sync.py`：增量文档同步（MD5 校验和）
- `src/prompts/templates.py`：Prompt 模板
- `src/models/schemas.py`：Pydantic 数据模型
- `src/api/main.py`：FastAPI 服务
- `scripts/`：索引脚本、启动脚本、CLI 问答
