# 知识库 Agent 项目计划

## 项目目标

构建一个基于本地 LLM（DeepSeek R1 7B + Ollama）的知识库智能问答 Agent，支持私有文档的检索增强生成（RAG）。

## 知识源

- 目录：`/Users/wei.tao/Desktop/Data Confluence`
- 文件类型：Markdown（约 50 个文件，200+ KB）
- 分类：Agent、Anomaly Detection、Cursor经验、LLM、RAG+Memory、Tech Doc
- 特点：文件会不定期更新、删除、新增，需增量同步

## 任务清单

### 阶段一：基础设施搭建

- [x] 创建项目目录结构 `done`
- [x] 创建开发规范 rules 文件 `done`
- [x] 拉取 DeepSeek R1 7B 模型（Ollama）`in progress`
- [x] 创建 Python 依赖 requirements.txt `done`
- [x] 编写配置管理模块（pydantic-settings + .env）`done`

### 阶段二：核心 RAG Pipeline

- [x] 实现文档加载器（从 Data Confluence 读取 .md，排除隐藏目录）`done`
- [x] 实现文档切分器（Markdown 标题切分 + 递归字符切分）`done`
- [x] 实现向量存储（ChromaDB + Ollama nomic-embed-text）`done`
- [x] 实现 LLM 客户端（Ollama REST API，同步/异步）`done`
- [x] 实现 Prompt 模板管理 `done`
- [x] 实现 RAG Pipeline 完整编排 `done`

### 阶段三：文档同步与 API 服务

- [x] 实现增量文档同步（MD5 校验和比对）`done`
- [x] 实现后台定时同步（可配置间隔）`done`
- [x] 搭建 FastAPI 服务（问答/同步/重建/状态接口）`done`
- [x] 创建索引脚本、启动脚本、CLI 问答工具 `done`

### 阶段四：测试与验证

- [ ] 安装依赖并验证启动 `not started`
- [ ] 执行首次全量索引 `not started`
- [ ] 端到端问答测试 `not started`

### 阶段五：优化迭代

- [ ] 调优 chunk_size 和 top_k 参数 `not started`
- [ ] 优化 Prompt 模板提升回答质量 `not started`
- [ ] 添加单元测试和集成测试 `not started`
- [ ] 性能测试（索引速度、查询延迟）`not started`
