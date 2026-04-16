# 知识库 Agent 变更日志

## 2026-04-16（用户账号体系 v3.0）

### 🔐 用户认证系统
- ✅ **JWT认证**：基于JSON Web Token的用户会话管理
- ✅ **邮箱注册/登录**：支持用户邮箱密码注册和登录
- ✅ **密码安全**：使用bcrypt算法加密用户密码
- ✅ **本地存储**：基于JSON文件的用户数据持久化

### 💬 对话历史管理（升级）
- ✅ **用户隔离**：基于用户ID的对话记录完全隔离
- ✅ **会话限制**：每用户最多保存10条历史对话
- ✅ **Pin功能**：重要对话置顶，支持pin/unpin操作
- ✅ **新对话功能**：一键创建新对话会话
- ✅ **权限控制**：只有登录用户可以访问对话功能

### 🎨 前端UI升级
- ✅ **登录界面**：精美的认证模态框（AuthModal）
- ✅ **用户状态显示**：侧边栏显示当前用户信息
- ✅ **权限提示**：未登录用户的友好提示界面
- ✅ **会话管理**：集成+新对话按钮和对话历史

### 🛠 Ask工具集成
- ✅ **前端组件**：AskModal选项弹框界面
- ✅ **后端支持**：ask.py响应处理API
- ✅ **交互机制**：AI与用户的选项式沟通工具
- ✅ **Markdown渲染**：支持富文本问题显示

### 📚 文档规范化
- ✅ **README更新**：按照项目规范更新所有模块README
- ✅ **.cursor目录**：新增专门的配置目录说明文档
- ✅ **功能说明**：完整记录新增功能和技术细节

### 🏗 后端架构扩展
**新增核心模块**：
- `src/core/user_manager.py` - 用户管理和JWT认证
- `src/core/auth_deps.py` - FastAPI认证依赖注入
- `src/core/conversation_manager.py` - 对话历史管理（用户隔离升级）

**API接口扩展**：
- `POST /auth/register` - 用户注册
- `POST /auth/login` - 用户登录  
- `GET /auth/me` - 获取当前用户信息
- `POST /chat/new` - 创建新对话
- `POST /ask/response` - Ask工具响应处理
- `GET /ask/check` - 检查Ask请求状态

**数据模型升级**：
- 用户认证相关：`UserCreate`, `UserLogin`, `User`, `Token`
- Ask工具相关：`AskResponseRequest`
- 对话模型升级：添加`user_id`字段

### 🔧 前端架构优化
**新增组件**：
- `AuthModal.jsx` - 用户认证界面
- `AskModal.jsx` - Ask工具选项弹框
- 升级现有组件支持用户状态管理

**API客户端升级**：
- JWT token自动管理
- 认证API集成
- Ask工具API支持

**状态管理优化**：
- 全局用户状态管理
- 认证模态框状态控制
- Ask工具交互状态

### 📊 技术亮点
- 🔒 **安全性**：JWT + bcrypt双重安全保障
- 👥 **用户体验**：无缝的登录注册流程
- 🎯 **隐私保护**：用户数据完全隔离
- ⚡ **性能优化**：本地JSON存储，响应迅速
- 🎨 **UI一致性**：深色主题统一设计风格

### 🧪 功能验证
- ✅ 用户注册/登录流程测试
- ✅ JWT token认证机制验证
- ✅ 用户对话历史隔离测试
- ✅ Pin/删除/新对话功能测试
- ✅ Ask工具集成功能验证
- ✅ 前后端认证状态同步测试

---

## 2026-04-16（历史对话功能 v2.0）

### 核心功能新增

- **侧边栏历史对话**：显示最近20个对话，支持置顶功能
- **对话持久化**：自动保存问答记录（排除thinking过程）
- **历史对话管理**：支持置顶/取消置顶、删除对话、点击回看

### 后端API扩展

- **新增数据模型**：`ConversationManager`、`Conversation`、`ConversationMessage`等
- **新增API端点**：
  - `POST /api/v1/conversations`：保存对话
  - `GET /api/v1/conversations`：获取对话列表
  - `GET /api/v1/conversations/{id}`：获取单个对话
  - `PUT /api/v1/conversations/{id}`：更新对话（置顶）
  - `DELETE /api/v1/conversations/{id}`：删除对话
- **数据存储**：使用本地JSON文件 `./data/conversations.json`

### 前端UI优化

- **新增组件**：`ConversationHistory.jsx` 历史对话列表
- **侧边栏增强**：集成历史对话区域，支持滚动浏览
- **交互体验**：悬停显示操作按钮、置顶标识、时间显示
- **自动保存**：问答完成后自动保存到历史记录

### 技术亮点

- **智能排序**：置顶对话优先显示，其他按时间倒序
- **数据同步**：前后端状态实时同步，操作即时生效
- **用户体验**：点击历史对话自动加载到主界面
- **存储优化**：历史记录仅保留最终答案，不包含thinking过程

### 受影响文件

#### 后端
- `src/models/schemas.py`：新增对话相关数据模型
- `src/core/conversation_manager.py`：新增对话管理核心逻辑
- `src/api/routes.py`：新增对话相关API路由
- `src/api/main.py`：集成ConversationManager依赖注入

#### 前端
- `frontend/src/api.js`：新增对话相关API客户端函数
- `frontend/src/components/ConversationHistory.jsx`：新增历史对话组件
- `frontend/src/components/Sidebar.jsx`：集成历史对话显示
- `frontend/src/components/ChatPanel.jsx`：集成自动保存和历史加载
- `frontend/src/App.jsx`：协调对话状态管理

### 测试验证

- ✅ 对话创建和保存功能正常
- ✅ 历史对话列表获取正常  
- ✅ 置顶/取消置顶功能正常
- ✅ 删除对话功能正常
- ✅ 前后端API通信正常
- ✅ 前端开发服务器正常启动

## 2026-04-16（知识库 v1.2 升级）

### 知识库更新

- **知识库路径迁移**：从 `./knowledge/` 迁移到 `./agent kb v1.2/`
- **内容显著更新**：文档数从 96 个减少到 79 个，总大小从 552KB 增加到 2.0MB
- **分类结构优化**：包含 Agent、Anomaly detection - sharkAI、Credit Bot - Datajoi、Cursor related、LLM、MCP、RAG+Memory 等类别
- **新增文档**：包括 `knowledge_inventory.csv` 审计报告和 `audit_report.md` 等

### 配置更新

- **`.env`**：`KNOWLEDGE_SOURCE_DIR` 从 `./knowledge` 更新为 `./agent kb v1.2`
- **`.env.example`**：同步更新知识库路径配置
- **`config/settings.py`**：默认知识库路径更新
- **`README.md`**：更新项目结构说明和配置文档

### 索引重建

- **完全重建向量数据库**：79 个文档 → 1254 个检索 chunk + 696 个上下文 chunk
- **索引性能**：约 4.5 分钟完成全量重建（包含文档加载、切分、Embedding 计算、向量存储）
- **功能验证**：CLI 和 API 问答功能正常工作

### 受影响文件

- 配置文件：`.env`、`.env.example`、`config/settings.py`、`README.md`
- 向量数据库：完全重建，更新所有文档的 chunk 和 embedding
- 知识库目录：从 `knowledge/` 迁移到 `agent kb v1.2/`

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
