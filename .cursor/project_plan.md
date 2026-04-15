# 知识库 Agent 项目计划

## 项目目标

构建一个基于本地 LLM（DeepSeek R1 14B + Ollama）的知识库智能问答 Agent，支持私有文档的检索增强生成（RAG）。

## 知识源

- 目录：`/Users/wei.tao/Desktop/Data Confluence`
- 文件类型：Markdown（约 50 个文件，200+ KB）
- 分类：Agent、Anomaly Detection、Cursor经验、LLM、RAG+Memory、Tech Doc
- 特点：文件会不定期更新、删除、新增，需增量同步

## 任务清单

### 阶段一：基础设施搭建

- [x] 创建项目目录结构 `done`
- [x] 创建开发规范 rules 文件 `done`
- [x] 配置 LLM 模型（使用本地已有的 deepseek-r1:14b）`done`
- [x] 创建 Python 依赖 requirements.txt `done`
- [x] 编写配置管理模块（pydantic-settings + .env）`done`

### 阶段二：核心 RAG Pipeline

- [x] 实现文档加载器（从 Data Confluence 读取 .md，排除隐藏目录）`done`
- [x] 实现文档切分器（Markdown 标题切分 + 递归字符切分）`done`
- [x] 实现向量存储（ChromaDB + Ollama bge-m3）`done`
- [x] 实现 LLM 客户端（Ollama REST API，同步/异步）`done`
- [x] 实现 Prompt 模板管理 `done`
- [x] 实现 RAG Pipeline 完整编排 `done`

### 阶段三：文档同步与 API 服务

- [x] 实现增量文档同步（MD5 校验和比对）`done`
- [x] 实现后台定时同步（可配置间隔）`done`
- [x] 搭建 FastAPI 服务（问答/同步/重建/状态接口）`done`
- [x] 创建索引脚本、启动脚本、CLI 问答工具 `done`

### 阶段四：测试与验证

- [x] 安装依赖并验证启动 `done`
- [x] 执行首次全量索引（49 文档 → 293 chunk，耗时 28s） `done`
- [x] 端到端问答测试（CLI + API 均通过） `done`

### 阶段五：文档关系图（Hook）

- [x] 编写 scripts/build_relations.py 扫描脚本 `done`
- [x] 生成 docs/doc_relations.json 关系映射文件 `done`
- [x] 生成 docs/doc_graph.md Mermaid 可视化关系图 `done`
- [x] 将引用关系集成到 RAG pipeline 的 metadata 中 `done`

### 阶段六：RAG 质量优化

- [x] 更换 Embedding 模型为 bge-m3（多语言优化）`done`
- [x] 实现 Parent Document Retrieval（小 chunk 检索 + 大 chunk 上下文）`done`
- [x] 新增检索结果最低分阈值 0.5 `done`
- [x] 新增同文件去重（最多 3 个 chunk）`done`
- [x] 调低 temperature 至 0.2 `done`
- [x] Hook 关系融入 Prompt 上下文 `done`
- [x] 重建索引并验证效果（bge-m3 已下载并切换）`done`

### 阶段七：前端 UI + 流式优化

- [x] 创建 React + Vite + Tailwind 前端项目 `done`
- [x] 实现暗色系聊天 UI（消息列表、输入框、来源引用）`done`
- [x] 对接后端 API + 后端添加 CORS 支持 `done`
- [x] 支持用户停止提问（AbortController + 恢复输入框）`done`
- [x] ThinkingIndicator 组件（10s 步骤 + 1s 频闪百分比）`done`
- [x] 后端流式 API（`/ask/stream` + NDJSON + StreamingResponse）`done`
- [x] 前端流式渲染（ReadableStream + RAF 批量渲染）`done`
- [x] 思考过程折叠框（灰色、自动展开/收起、内容滚动）`done`
- [x] 流式打字光标 + 答案逐字展示 `done`

### 阶段八：后续迭代

- [ ] 添加单元测试和集成测试 `not started`
- [ ] 性能测试（索引速度、查询延迟）`not started`
- [ ] 爬取外部链接内容（full_content 模式，保存为 Markdown）`not started`
- [ ] 文档预处理（清洗 Confluence 元数据噪音）`not started`
- [ ] Query Rewriting / HyDE 查询预处理 `not started`
