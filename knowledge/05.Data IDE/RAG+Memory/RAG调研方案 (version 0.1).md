# RAG调研方案 (version 0.1)

> **Page ID**: 2742657833
> **URL**: https://confluence.shopee.io/pages/viewpage.action?pageId=2742657833

[向量数据库调研对比](https://confluence.shopee.io/pages/viewpage.action?pageId=2742657412#vectordb)
==========================================================================================

[RAG 框架调研对比](https://confluence.shopee.io/pages/viewpage.action?pageId=2742657412#rag)
======================================================================================

[知识图谱与向量数据库](https://confluence.shopee.io/pages/viewpage.action?pageId=2749045713)
==================================================================================

**公司内项目调研**
===========

|  |  |  |
| --- | --- | --- |
| 平台 | 链接 | 向量数据库方案 |
| SMART | <https://space-next.shopee.io/reliability/smart/main/workspace> | Milvus |
| Sea Alpha Knowledge | <https://knowledge.alpha.insea.io/> | Qdrant |
| Seatalk AI Bot | <https://aichat.infra.shopee.io/bot/botList> | Milvus |
| Compass | <https://compass.llm.shopee.io/> | ES |

**架构设计方案**
==========

**整体方案**
--------

![image2025-5-29_15-11-57.png](https://confluence.shopee.io/download/attachments/2742657833/image2025-5-29_15-11-57.png)

**知识库构建流程**
-----------

**![image-2.png](https://www.dailydoseofds.com/content/images/2024/11/image-2.png)**

**[知识库构建流程中的潜在问题](https://confluence.shopee.io/pages/viewpage.action?pageId=2749046146)**
-----------------------------------------------------------------------------------------

### **数据采集**

* 来源：公司文档、网页、数据库、API接口
* 工具：

+ 爬虫（Scrapy）
+ API集成
+ 中台数据同步
+ Chrome插件/API（sea alpha）
+ Web操作录入（seatalk ai bot）

### **数据预处理**

* 清洗：去噪、去HTML标签、转码
* 分段：按段/章节/语义分割（Langchain/TextSplitter）

* 格式化：统一文本格式、元信息打标签
* 非文本数据的处理？

+ Seatalk ai bot（暂不支持图片，成本原因）

### **向量化处理**

* 文本嵌入模型：

+ OpenAI text-embedding-ada-002
+ BGE、E5、Cohere、MiniLM等

* 向量库选型：

+ 本地部署：Milvus、Qdrant、Faiss、Weaviate

### **检索与召回**

* 检索方式：

+ 向量检索（Semantic Search）
+ 混合检索（Hybrid Search + BM25）

* 增强策略：

+ 多轮检索
+ 多模态支持（图像、代码片段）

### **与LLM集成**

* 框架：Langchain / LlamaIndex / Semantic Kernel / Haystack
* 通过MCP将知识库集成到AI IDE中
* 工作流程：

+ 用户输入 → 向量检索 → 上下文拼接 → Prompt注入 → LLM生成回答
