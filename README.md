# 知识库 Agent

基于本地 LLM 的私有知识库智能问答系统，采用 RAG（检索增强生成）架构。

- **GitHub 仓库**：https://github.com/tw544814347/knowledge-agent
- **在线前端**：https://tw544814347.github.io/knowledge-agent/

> 在线前端需要后端 API 运行（本地启动后端 + ngrok 穿透，或设置 `VITE_API_URL` 环境变量）

## 技术栈

- **LLM 推理**：Ollama + DeepSeek R1 14B
- **Embedding**：bge-m3（BAAI 多语言，1024 维，通过 Ollama 调用）
- **向量数据库**：ChromaDB（余弦相似度，Parent Document Retrieval）
- **文档切分**：Markdown 标题切分 + 双层 chunk（小 chunk 检索 + 大 chunk 上下文）
- **后端框架**：Python + FastAPI
- **前端界面**：React + Vite + Tailwind CSS（暗色系聊天 UI）
- **文档同步**：MD5 校验和增量同步

## 前置条件

1. 安装 [Ollama](https://ollama.ai)
2. 拉取所需模型：

```bash
ollama pull deepseek-r1:14b
ollama pull bge-m3
```

3. Python >= 3.10
4. Node.js >= 18（前端开发需要）

## 快速开始

### 后端

```bash
# 安装依赖
pip install -r requirements.txt

# 首次全量索引
python scripts/index_docs.py

# 启动 API 服务
python scripts/run_server.py

# 或使用命令行问答
python scripts/query_cli.py
```

### 前端

```bash
cd frontend
npm install
npm run dev
```

访问 `http://localhost:3000` 打开聊天界面。

### 外部访问（GitHub Pages + ngrok）

项目前端已部署到 GitHub Pages，外部可通过 https://tw544814347.github.io/knowledge-agent/ 访问。

由于后端（Ollama LLM）运行在本地，需要 ngrok 内网穿透才能让外部前端连接到本地后端。**每次开机后需执行：**

```bash
# 1. 启动后端 API
cd ~/Desktop/知识库\ agent && python scripts/run_server.py &

# 2. 启动 ngrok 内网穿透（将本地 8000 端口暴露到公网）
ngrok http 8000 &
```

启动后确认：
- 后端健康检查：`curl http://localhost:8000/health`
- ngrok 状态面板：http://localhost:4040

> **注意**：ngrok 免费版的 URL 通常保持不变（当前为 `kerosene-duo-swaddling.ngrok-free.dev`）。如果 URL 发生变化，需要更新 GitHub 仓库变量并重新部署前端：
> ```bash
> gh variable set VITE_API_URL --body "https://新的ngrok地址"
> gh workflow run deploy-pages.yml
> ```

## API 接口

启动服务后访问 `http://localhost:8000/docs` 查看 Swagger 文档。

| 接口 | 方法 | 说明 |
|------|------|------|
| `/health` | GET | 健康检查（含 LLM 和 Embedding 模型信息） |
| `/api/v1/ask` | POST | 知识库问答 |
| `/api/v1/ask/stream` | POST | 流式知识库问答（NDJSON） |
| `/api/v1/sync` | POST | 增量文档同步 |
| `/api/v1/rebuild` | POST | 重建全量索引 |
| `/api/v1/status` | GET | 索引状态查询 |

## 项目结构

```
知识库 agent/
├── rules/                          # 开发规范
│   └── knowledge-agent.mdc
├── config/                         # 配置
│   └── settings.py
├── src/
│   ├── core/                       # 核心模块
│   │   ├── document_loader.py      # 文档加载
│   │   ├── document_processor.py   # 双层 chunk 切分
│   │   ├── vector_store.py         # ChromaDB 向量存储 + bge-m3 Embedding
│   │   ├── llm_client.py           # Ollama LLM 调用（同步/异步 + 重试）
│   │   ├── rag_pipeline.py         # RAG 流程编排
│   │   └── doc_sync.py             # 增量文档同步
│   ├── api/                        # FastAPI 接口
│   ├── models/                     # Pydantic 数据模型
│   └── prompts/                    # Prompt 模板
├── scripts/                        # 脚本工具
│   ├── index_docs.py               # 全量索引
│   ├── run_server.py               # 启动 API 服务
│   ├── query_cli.py                # CLI 交互式问答
│   └── build_relations.py          # 文档关系图构建
├── frontend/                       # React 前端
│   └── src/
├── agent kb v1.2/                 # 内置知识库文件（Markdown）
├── docs/                           # 文档关系映射（自动生成）
├── data/vectordb/                  # 向量数据库持久化（不提交）
├── .github/workflows/              # GitHub Actions 自动部署
├── .env                            # 环境配置（不提交）
└── requirements.txt                # Python 依赖
```

## 配置说明

复制 `.env.example` 为 `.env` 并根据需要修改：

- `KNOWLEDGE_SOURCE_DIR`：知识文档源目录路径（默认 `./agent kb v1.2`）
- `LLM_MODEL`：LLM 模型名称（默认 `deepseek-r1:14b`）
- `EMBEDDING_MODEL`：Embedding 模型（默认 `bge-m3`）
- `CHUNK_SIZE` / `PARENT_CHUNK_SIZE`：双层 chunk 切分参数
- `TOP_K`：检索返回数量（默认 8）
- `MIN_SCORE`：检索最低相关度阈值（默认 0.5）
- `SYNC_INTERVAL`：后台自动同步间隔（秒）
