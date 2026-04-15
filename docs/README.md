# docs — 项目文档

存放项目相关的文档资料。

## 目录结构

```
docs/
└── knowledge/    # 知识文档存放（可选，项目主要知识源在 Data Confluence）
```

## 说明

本项目的知识文档主要来源是外部目录 `/Users/wei.tao/Desktop/Data Confluence`，由 `DocumentLoader` 自动加载。

`docs/knowledge/` 目录可用于存放额外的补充文档，但默认不参与索引。如需将此目录也纳入索引，需在 `.env` 中修改 `KNOWLEDGE_SOURCE_DIR` 配置。
