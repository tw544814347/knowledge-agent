# src（Source）源代码目录

`src` 是 **Source Code** 的缩写，即"源代码"。本目录存放知识库 Agent 的全部业务代码，是项目的核心。

## 整体架构

```
用户提问
   │
   ▼
┌─────────┐     ┌──────────────┐     ┌─────────────┐     ┌──────────┐
│  API 层  │ ──▶ │  RAG Pipeline │ ──▶ │  向量检索     │ ──▶ │ LLM 生成  │
│ (FastAPI)│     │  (流程编排)    │     │ (ChromaDB)   │     │(DeepSeek)│
└─────────┘     └──────────────┘     └─────────────┘     └──────────┘
                       │                                       │
                       ▼                                       ▼
                ┌──────────────┐                        ┌──────────┐
                │  文档加载+切分  │                        │ Prompt   │
                │  (Loader/     │                        │ 模板管理  │
                │   Processor)  │                        └──────────┘
                └──────────────┘
```

## 目录结构说明

```
src/
├── core/           # 核心业务逻辑（最重要的部分）
├── api/            # HTTP 接口层（FastAPI 路由）
├── models/         # 数据模型定义（Pydantic）
├── prompts/        # Prompt 模板管理
├── utils/          # 通用工具函数
└── tests/          # 测试文件
```

### core/ — 核心逻辑

RAG 知识库的全部核心能力都在这里：

| 文件 | 职责 | 关键类/函数 |
|------|------|------------|
| `document_loader.py` | 从 Data Confluence 加载 .md 文件 | `DocumentLoader` — 递归扫描文件，排除 `.specstory` 等隐藏目录 |
| `document_processor.py` | 将文档切分为适合向量化的 chunk | `DocumentProcessor` — 两阶段切分：先按 Markdown 标题，再按字符长度 |
| `vector_store.py` | 向量数据库读写 | `VectorStore` — ChromaDB 管理，`OllamaEmbedding` — 调用 nomic-embed-text 生成向量 |
| `llm_client.py` | 调用 DeepSeek R1 7B 生成回答 | `LLMClient` — 通过 Ollama REST API，支持同步/异步 |
| `rag_pipeline.py` | RAG 完整流程编排 | `RAGPipeline` — 串联加载→切分→检索→生成的全流程 |
| `doc_sync.py` | 增量文档同步 | `DocumentSyncer` — MD5 校验和比对，检测文件增删改，后台定时同步 |

### api/ — HTTP 接口层

对外暴露的 REST API，基于 FastAPI：

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/query` | POST | 知识库问答（输入问题，返回 AI 回答 + 参考来源） |
| `/api/status` | GET | 查看索引状态（chunk 总数、最近同步时间） |
| `/api/sync` | POST | 手动触发文档增量同步 |
| `/api/reindex` | POST | 全量清空并重建索引 |
| `/health` | GET | 健康检查 |

### models/ — 数据模型

使用 Pydantic 定义请求/响应的数据结构：

- `QueryRequest` — 问答请求（question + top_k）
- `QueryResponse` — 问答响应（answer + sources）
- `IndexStatusResponse` — 索引状态
- `SyncResponse` — 同步结果

### prompts/ — Prompt 模板

管理所有发送给 LLM 的 Prompt：

- **System Prompt**：定义 AI 角色、回答规则、输出格式
- **QA Prompt 模板**：将检索到的文档上下文 + 用户问题组装成完整 Prompt
- **上下文构建**：将检索结果格式化为带来源标注的参考文档

### utils/ — 工具函数

存放通用的辅助函数（日志配置、文本清洗等）。

### tests/ — 测试

使用 pytest 编写的单元测试和集成测试。

## 数据流向

```
1. 文档入库流程（离线）:
   Data Confluence/*.md → DocumentLoader → DocumentProcessor → VectorStore(ChromaDB)

2. 问答流程（在线）:
   用户问题 → VectorStore.query() → Top-K chunks → Prompt模板 → LLMClient → 回答

3. 增量同步流程（后台）:
   定时扫描 → MD5比对 → 变更文件重新 加载→切分→入库
```

## 技术要点

- **Python 3.10+**，所有函数必须添加类型注解（Type Hints）
- **异步优先**：API 层使用 `async/await`，LLM 调用支持异步
- **配置外置**：所有参数通过 `.env` + `config/settings.py` 管理，不硬编码
- **日志完善**：使用 `loguru`，记录文档加载、向量写入、LLM 调用等关键环节
