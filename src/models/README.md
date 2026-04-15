# models — 数据模型

使用 Pydantic 定义 API 请求和响应的数据结构，提供自动校验和文档生成。

## 文件说明

| 文件 | 职责 |
|------|------|
| `schemas.py` | 全部 Pydantic 数据模型 |

## 模型清单

| 模型 | 用途 | 关键字段 |
|------|------|----------|
| `QueryRequest` | 问答请求 | `question`（问题）, `top_k`（检索数量） |
| `QueryResponse` | 问答响应 | `answer`（回答）, `sources`（参考来源列表） |
| `SourceInfo` | 引用来源 | `filename`, `category`, `score`, `section` |
| `IndexStatusResponse` | 索引状态 | `total_chunks`, `source_dir`, `last_sync` |
| `SyncResponse` | 同步结果 | `added`, `updated`, `deleted`, `total_chunks` |
