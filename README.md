# 知识库 Agent

基于本地 LLM 的私有知识库智能问答系统，采用 RAG（检索增强生成）架构。

## 技术栈

- **LLM 推理**：Ollama + DeepSeek R1 7B
- **Embedding**：nomic-embed-text（Ollama）
- **向量数据库**：ChromaDB（余弦相似度）
- **文档切分**：Markdown 标题切分 + 递归字符切分
- **后端框架**：Python + FastAPI
- **文档同步**：MD5 校验和增量同步

## 前置条件

1. 安装 [Ollama](https://ollama.ai)
2. 拉取所需模型：

```bash
ollama pull deepseek-r1:7b
ollama pull nomic-embed-text
```

3. Python >= 3.10

## 快速开始

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

## API 接口

启动服务后访问 `http://localhost:8000/docs` 查看 Swagger 文档。

| 接口 | 方法 | 说明 |
|------|------|------|
| `/health` | GET | 健康检查 |
| `/api/v1/ask` | POST | 知识库问答 |
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
│   │   ├── document_processor.py   # 文档切分
│   │   ├── vector_store.py         # 向量存储
│   │   ├── llm_client.py           # LLM 调用
│   │   ├── rag_pipeline.py         # RAG 编排
│   │   └── doc_sync.py             # 增量同步
│   ├── api/                        # API 接口
│   ├── models/                     # 数据模型
│   └── prompts/                    # Prompt 模板
├── scripts/                        # 脚本工具
│   ├── index_docs.py               # 全量索引
│   ├── run_server.py               # 启动服务
│   └── query_cli.py                # CLI 问答
├── data/vectordb/                  # 向量数据库
├── .env                            # 环境配置
└── requirements.txt                # Python 依赖
```

## 配置说明

复制 `.env.example` 为 `.env` 并根据需要修改：

- `KNOWLEDGE_SOURCE_DIR`：知识文档源目录路径
- `LLM_MODEL`：LLM 模型名称
- `CHUNK_SIZE` / `CHUNK_OVERLAP`：文档切分参数
- `TOP_K`：检索返回数量
- `SYNC_INTERVAL`：后台自动同步间隔（秒）
