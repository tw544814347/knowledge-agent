# 文档关系图

```mermaid
flowchart LR
    subgraph Agent [Agent]
        n0["Data Chatbot - DataJoi(multi-agent version)"]
        n1["DataJoi 评测体系技术方案"]
        n2["Deepwiki Agent"]
        n3["Eight Honors and Eight Shames"]
        n4["Multi-Agent vs Workflow"]
        n5["Prompt Optimization Agent"]
        n6["Protobuf Chatbot"]
    end
    subgraph Anomaly_Detection [Anomaly Detection]
        n7["2025-12交接索引"]
        n8["Anomaly Detection"]
        n9["Backend Service"]
        n10["PRD-Shark"]
        n11["异常检测技术调研"]
        n12["异常检测问题记录"]
        n13["异常检测需求收集"]
        n14["异常检测项目排期"]
        n15["时序预测"]
    end
    subgraph Cursor经验 [Cursor经验]
        n16["Cursor Rules"]
        n17["MCP分享"]
        n18["Prompt分享"]
        n19["其他工具"]
        n20["开发套路分享"]
    end
    subgraph LLM [LLM]
        n21["Application & Platform"]
        n22["Basic Concept"]
        n23["Project"]
    end
    subgraph RAGPlusMemory [RAG+Memory]
        n24["Langchain V.S. LlamaIndex"]
        n25["RAG应用案例"]
        n26["RAG有效性评估"]
        n27["RAG调研方案 (version 0.1)"]
        n28["SuperRAG"]
        n29["embabel"]
        n30["kb 里程碑"]
        n31["md test file"]
        n32["milvus V.S. Qdrant"]
        n33["vector db & RAG"]
        n34["不同角色RAG需求"]
        n35["关键流程"]
        n36["文档解析方案对比"]
        n37["知识图谱与向量数据库"]
        n38["知识库构建流程中的潜在问题和解决方案"]
        n39["知识库系统收益评估方式"]
        n40["系统挑战"]
        n41["金融kb"]
        n42["非向量化方案"]
    end
    subgraph Tech_Doc [Tech Doc]
        n43["BE Entry Task"]
        n44["Bitmap64 统一序列化"]
        n45["Flink相关"]
        n46["Load Data From S3"]
        n47["大数据平台架构图"]
        n48["实时数据-entrytask"]
    end
    n27 -->|引用| n33
    n27 -->|引用| n37
    n27 -->|引用| n38
```

## 统计

| 指标 | 数值 |
|------|------|
| 文档总数 | 49 |
| 文档间交叉引用 | 3 |
| 外部链接 | 70 |
| Confluence 图片 | 9 |
| 分类数 | 6 |

## 交叉引用详情

| 来源文档 | 引用目标 |
|----------|----------|
| 05.Data IDE/RAG+Memory/RAG调研方案 (version 0.1).md | 05.Data IDE/RAG+Memory/vector db & RAG.md |
| 05.Data IDE/RAG+Memory/RAG调研方案 (version 0.1).md | 05.Data IDE/RAG+Memory/知识图谱与向量数据库.md |
| 05.Data IDE/RAG+Memory/RAG调研方案 (version 0.1).md | 05.Data IDE/RAG+Memory/知识库构建流程中的潜在问题和解决方案.md |