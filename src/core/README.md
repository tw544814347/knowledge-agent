# core — 核心业务逻辑

RAG 知识库 Agent 的全部核心能力，包含文档处理、向量存储、LLM 调用和流程编排。

## 文件说明

| 文件 | 职责 | 关键类 |
|------|------|--------|
| `document_loader.py` | 从 Data Confluence 递归加载 .md 文件 | `DocumentLoader` — 自动排除 `.specstory`/`.vscode` 等隐藏目录 |
| `document_processor.py` | 将长文档切分为适合向量化的 chunk | `DocumentProcessor` — 两阶段策略：Markdown 标题切分 → 递归字符切分 |
| `vector_store.py` | 向量数据库的读写操作 | `VectorStore` — ChromaDB 管理；`OllamaEmbedding` — 调用 nomic-embed-text |
| `llm_client.py` | 调用本地 LLM 生成回答 | `LLMClient` — 通过 Ollama REST API 调用 DeepSeek R1 7B，支持同步/异步 |
| `rag_pipeline.py` | RAG 完整流程编排 | `RAGPipeline` — 串联 加载→切分→检索→Prompt注入→生成 |
| `doc_sync.py` | 增量文档同步 | `DocumentSyncer` — MD5 校验和比对，后台定时检测文件变更 |
| `user_manager.py` | 用户管理和认证 | `UserManager` — JWT认证、密码加密、用户CRUD操作 |
| `conversation_manager.py` | 对话历史管理 | `ConversationManager` — 用户对话记录、Pin功能、会话限制 |
| `auth_deps.py` | 认证依赖注入 | FastAPI依赖函数 — JWT解析、用户认证、权限验证 |

## 数据流向

```
文档入库:  DocumentLoader → DocumentProcessor → VectorStore
问答流程:  VectorStore.query() → Prompt模板 → LLMClient.generate()
增量同步:  DocumentSyncer → (比对MD5) → 变更文件重新入库
用户认证:  用户登录 → JWT生成 → 请求验证 → 权限检查
对话管理:  用户发起对话 → 对话记录保存 → 历史查询 → Pin/删除管理
```

## 依赖关系

```
rag_pipeline.py
├── document_loader.py
├── document_processor.py
├── vector_store.py
├── llm_client.py
└── (引用 prompts/templates.py)

doc_sync.py
├── document_loader.py
├── document_processor.py
└── vector_store.py

user_manager.py
├── JWT 认证库 (python-jose)
├── 密码哈希库 (passlib)
└── 本地存储 (JSON文件)

conversation_manager.py
├── user_manager.py (用户验证)
└── 本地存储 (JSON文件)

auth_deps.py
├── user_manager.py
└── FastAPI 依赖注入
```
