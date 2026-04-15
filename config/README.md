# config — 配置管理

基于 `pydantic-settings` 的统一配置管理，从 `.env` 文件加载环境变量。

## 文件说明

| 文件 | 职责 |
|------|------|
| `settings.py` | 定义 `Settings` 类，集中管理所有可配置参数 |

## 配置项一览

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama 服务地址 |
| `LLM_MODEL` | `deepseek-r1:7b` | 推理模型 |
| `EMBEDDING_MODEL` | `nomic-embed-text` | Embedding 模型 |
| `KNOWLEDGE_SOURCE_DIR` | `/Users/.../Data Confluence` | 知识文档源目录 |
| `CHUNK_SIZE` | `512` | 文档切分大小（字符数） |
| `CHUNK_OVERLAP` | `64` | chunk 之间的重叠字符数 |
| `TOP_K` | `5` | 检索返回的文档数量 |
| `LLM_TEMPERATURE` | `0.3` | 生成温度（越低越确定） |
| `SYNC_INTERVAL` | `300` | 后台同步间隔（秒） |

## 使用方式

```python
from config.settings import settings

print(settings.llm_model)        # deepseek-r1:7b
print(settings.chunk_size)       # 512
```
