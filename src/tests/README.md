# tests — 测试文件

使用 pytest 编写的单元测试和集成测试。

## 测试规划

| 测试类型 | 覆盖范围 | 状态 |
|---------|---------|------|
| 单元测试 | DocumentLoader、DocumentProcessor 的切分逻辑 | 待开发 |
| 单元测试 | Prompt 模板的上下文构建 | 待开发 |
| 集成测试 | RAG Pipeline 端到端流程（检索 → 生成） | 待开发 |
| 集成测试 | 文档同步增量更新 | 待开发 |

## 运行方式

```bash
# 在项目根目录执行
pytest src/tests/ -v
```
