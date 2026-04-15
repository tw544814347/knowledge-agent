# scripts — 脚本工具

可独立运行的命令行脚本，用于文档索引、服务启动和交互式问答。

## 脚本列表

| 脚本 | 用途 | 运行方式 |
|------|------|----------|
| `index_docs.py` | 全量索引：加载所有文档 → 切分 → 写入向量库 | `python scripts/index_docs.py` |
| `run_server.py` | 启动 FastAPI 服务（含热重载） | `python scripts/run_server.py` |
| `query_cli.py` | 命令行交互式问答 | `python scripts/query_cli.py` |

## 使用顺序

```
1. 首次使用：python scripts/index_docs.py   # 先建立索引
2. 启动服务：python scripts/run_server.py    # API 方式使用
   或
   命令行：  python scripts/query_cli.py     # CLI 方式使用
```
