# api — HTTP 接口层

基于 FastAPI 的 REST API 服务，对外暴露知识库的问答、同步和管理能力。

## 文件说明

| 文件 | 职责 |
|------|------|
| `main.py` | FastAPI 应用入口，包含生命周期管理、中间件配置和全部路由 |

## 接口列表

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/query` | 知识库问答 — 输入问题，返回 AI 回答 + 参考来源 |
| GET | `/api/status` | 索引状态 — 查看 chunk 总数、最近同步时间 |
| POST | `/api/sync` | 手动同步 — 立即触发增量文档同步 |
| POST | `/api/reindex` | 全量重建 — 清空并重新索引所有文档 |
| GET | `/health` | 健康检查 |

## 生命周期

服务启动时（`lifespan`）：
1. 初始化 `RAGPipeline` 和 `DocumentSyncer`
2. 若向量库为空，自动执行首次全量索引
3. 启动后台定时同步

服务关闭时：停止后台同步线程。
