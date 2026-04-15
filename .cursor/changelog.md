# 知识库 Agent 变更日志

## 2026-04-15（GitHub 部署 + 知识库内置）

### GitHub 仓库

- 创建 Public 仓库 [tw544814347/knowledge-agent](https://github.com/tw544814347/knowledge-agent)
- 前端自动部署到 GitHub Pages：https://tw544814347.github.io/knowledge-agent/
- 添加 `.github/workflows/deploy-pages.yml` GitHub Actions 工作流（push main 自动构建部署）

### 知识库内置

- 将外挂知识库 `/Users/wei.tao/Desktop/Data Confluence` 复制到项目内 `knowledge/` 目录（96 个文件）
- `.env`、`.env.example`、`config/settings.py` 路径从绝对路径改为 `./knowledge`
- 清理 `.specstory`、`.vscode`、`.DS_Store` 等隐藏文件

### 前端适配

- `api.js`：API_BASE 支持 `VITE_API_URL` 环境变量（部署时指向 ngrok 后端 URL）
- `vite.config.js`：`base` 支持 GitHub Pages 子路径 `/knowledge-agent/`

### .gitignore 完善

- 新增 `node_modules/`、`frontend/dist/`、`*.log`、`data/checksums.json` 等排除规则

### 待完成

- ngrok 内网穿透配置（安装完成，待用户提供 authtoken 后启用）

## 2026-04-15（流式 API + 前端实时渲染）

### 核心优化：非流式 → 流式

原先前端发送问题后需等待 ~90 秒（LLM 全部生成完）才能看到任何内容。改为流式后：

| 阶段 | 改动前 | 改动后 |
|------|--------|--------|
| 首次反馈 | ~90s | ~2s（检索文件立即显示） |
| thinking 过程 | 不可见 | 灰色折叠框实时滚动 |
| 答案展示 | 一次性出现 | 逐字流式 + 闪烁光标 |

### 后端新增

- **`llm_client.py`**：新增 `stream_generate()` 方法，通过 httpx 流式读取 Ollama NDJSON，逐 token yield
- **`rag_pipeline.py`**：新增 `stream_query()` 方法，先 yield sources 再 yield tokens
- **`routes.py`**：新增 `POST /ask/stream` 流式端点，返回 `StreamingResponse`（NDJSON 格式）

### 前端改动

- **`api.js`**：新增 `askQuestionStream()`，使用 `ReadableStream` 读取 NDJSON 流
- **`ChatPanel.jsx`**：改用流式 API，`requestAnimationFrame` 批量渲染避免逐 token 重绘
- **`MessageBubble.jsx`**：
  - 初始加载阶段：显示 ThinkingIndicator（检索动画 + 进度条）
  - `<think>` 内容：灰色 `<details>` 折叠框，自动展开滚动，thinking 结束自动收起
  - 答案内容：Markdown 实时渲染 + 蓝色闪烁光标
- **`index.css`**：新增折叠框样式、脉冲点、流式光标、thinking 滚动条

### 规范更新

- **`rules/knowledge-agent.mdc`**：新增流式 API 规范（第 5 节）、前端开发规范（第 6 节）；技术栈表补充前端栈；目录结构补充 `frontend/` 和 `docs/`

## 2026-04-15（Embedding 切换 + 全局代码审查）

### Embedding 模型正式切换

- 从 `nomic-embed-text` 切换为 `bge-m3`（BAAI 多语言，1024 维）
- `.env`、`config/settings.py`、`.env.example` 全部更新为 `bge-m3`
- 使用 bge-m3 完成全量索引重建：85 个文档 → 1017 child chunk + 520 parent chunk

### 全局代码审查修复

| 问题 | 文件 | 修复方式 |
|------|------|----------|
| `doc_sync.py` 读校验和 JSON 无容错 | `src/core/doc_sync.py` | 增加 `JSONDecodeError` + `OSError` 异常捕获 |
| `templates.py` 中 `strip(' >')` 语义错误 | `src/prompts/templates.py` | 改为 `lstrip(' >')` |
| `llm_client.py` 文档注释引用 7B 模型 | `src/core/llm_client.py` | 更新为 "本地 LLM（默认 DeepSeek R1 14B）" |
| `index_docs.py` 未使用的 `CHECKSUM_FILE` 导入 | `scripts/index_docs.py` | 删除冗余导入 |
| `build_relations.py` 缺少 `node_modules` 排除 | `scripts/build_relations.py` | `EXCLUDE_DIRS` 补全 |
| `build_relations.py` category 规则与 loader 不一致 | `scripts/build_relations.py` | 统一为 `parts[0] if len(parts) > 1 else "uncategorized"` |
| `vector_store.py` Ollama embed 响应无校验 | `src/core/vector_store.py` | 增加 embeddings 字段存在性校验 |
| `/health` 端点缺少 embedding 模型信息 | `src/api/main.py` | 新增 `embedding_model` 返回字段 |

### 冗余清理

- 删除 `frontend/src/assets/react.svg`、`vite.svg`（未被引用的 Vite 脚手架残留）

### 文档更新

- `README.md`：全面更新技术栈（14B + bge-m3）、项目结构、配置说明
- `.env.example`：与当前 `.env` 对齐（bge-m3、双层 chunk 参数等）
- `project_plan.md`：更正项目目标描述、标记阶段六索引重建完成

### 端到端验证

- Health 端点正常：返回 `{"status": "ok", "model": "deepseek-r1:14b", "embedding_model": "bge-m3"}`
- 问答测试通过：bge-m3 检索相关度 0.52-0.61，LLM 生成结构化中文回答
- 向量库状态：child=1017, parent=520

## 2026-04-15（RAG 质量大幅优化）

### Embedding 模型升级

- 从 `nomic-embed-text`（英文主导，768 维）切换为 `bge-m3`（BAAI 多语言，1024 维）
- 中英混合术语语义理解大幅提升（如"向量数据库" ↔ "vector database"）

### Parent Document Retrieval

- 实现双层 chunk 策略：小 chunk（256 字符）用于精准检索，大 chunk（1536 字符）用于完整上下文
- `document_processor.py` 重写，生成 child + parent 两层 chunk
- `vector_store.py` 新增 parent collection，检索命中 child 后自动替换为 parent 内容

### 检索质量优化

- **最低分阈值**：`min_score=0.5`，低于此值的结果不送给 LLM
- **同文件去重**：同一文件最多保留 3 个 chunk（`max_chunks_per_doc=3`），避免单文件霸榜
- **粗检索扩大**：内部检索 `top_k * 3` 条候选后再过滤

### LLM 参数调优

- `temperature` 从 0.7 调低至 0.2，减少知识问答中的幻觉

### Hook 关系融入 Prompt

- `templates.py` 的 `build_context` 新增文档引用关系提示（"本文引用了 / 本文被引用于"）
- SYSTEM_PROMPT 新增规则：如果文档标注了关联文档，在回答末尾提示用户

### 受影响文件

- `config/settings.py`：新增 `parent_chunk_size`、`parent_chunk_overlap`、`min_score`、`max_chunks_per_doc`
- `.env`：同步更新所有新配置
- `src/core/document_processor.py`：完全重写（双层 chunk）
- `src/core/vector_store.py`：完全重写（parent collection、去重、分数过滤）
- `src/core/rag_pipeline.py`：适配新接口
- `src/core/doc_sync.py`：适配新的 `process_documents` 返回值
- `src/prompts/templates.py`：hook 关系融入上下文
- `scripts/index_docs.py`、`scripts/query_cli.py`：适配新接口

## 2026-04-15（文档关系图构建）

### 新增功能

- **scripts/build_relations.py**：文档关系图构建脚本，扫描 49 个 Markdown 文件，提取 pageId、交叉引用和所有超链接
- **docs/doc_relations.json**：结构化关系映射文件（49 文档、3 条交叉引用、70 个外部链接、9 张 Confluence 图片）
- **docs/doc_graph.md**：Mermaid 可视化关系图，按 6 个分类（Agent、RAG+Memory、LLM 等）分组展示

### RAG Pipeline 集成

- **document_loader.py**：加载文档时自动读取 `doc_relations.json`，将 `references_to`、`referenced_by`、`pageId` 注入 chunk metadata
- **rag_pipeline.py**：`_extract_sources` 方法增强，从 metadata 提取关联文档列表，写入 `SourceInfo.related_docs`
- **schemas.py**：`SourceInfo` 模型新增 `related_docs` 字段，问答结果可展示关联文档

### 关系图分析结果

- 发现 3 条文档间交叉引用（均从"RAG调研方案"引用其他 RAG 文档）
- 70 个外部链接标记为 `pending`（预留后续爬取）
- 9 张 Confluence 图片标记为 `auth_required`

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
