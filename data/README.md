# data — 数据存储

存放运行时生成的数据文件，不应提交到版本控制。

## 目录结构

```
data/
└── vectordb/     # ChromaDB 向量数据库持久化存储
```

## 说明

- `vectordb/` 目录由 ChromaDB 自动管理，包含向量索引和元数据
- 同步校验文件 `.checksums.json` 也存放在此目录下
- 如需重建索引，可删除 `vectordb/` 内容后执行 `python scripts/index_docs.py`
- 建议将 `data/` 目录加入 `.gitignore`
