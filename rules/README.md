# rules — 开发规范与项目规则

存放本项目的开发规范文件，所有协作者（包括 AI Agent）在开发时必须遵循。

## 文件说明

| 文件 | 职责 |
|------|------|
| `knowledge-agent.mdc` | 知识库 Agent 的完整开发规范 |

## 规范内容概览

- **技术栈定义**：Ollama + DeepSeek R1 7B + ChromaDB + FastAPI
- **RAG 架构范式**：文档预处理 → 向量化存储 → 检索召回 → 增强生成
- **文档规范（强制）**：每个母文件夹必须有 README.md
- **代码规范**：PEP 8、类型注解、async/await
- **配置管理**：.env + pydantic-settings
- **日志规范**：loguru，记录模型调用耗时和 token 用量
- **测试规范**：pytest，关键 RAG 流程需集成测试
- **目录结构约定**：完整的项目结构树
