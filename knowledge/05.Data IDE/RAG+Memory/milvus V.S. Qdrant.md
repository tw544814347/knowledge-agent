# milvus V.S. Qdrant

> **Page ID**: 2742657425
> **URL**: https://confluence.shopee.io/pages/viewpage.action?pageId=2742657425

Milvus vs. Qdrant 本地部署深度对比分析
============================

向量数据库是支持大规模语义检索、推荐和 RAG 应用的关键基础设施。以下从架构部署、资源效率、使用场景、性能、更新机制与生态六大方面对 Milvus 与 Qdrant 在本地部署场景中的表现进行系统对比，辅以企业实践参考。

—

1. 架构与部署模式
----------

| 项目 | Milvus | Qdrant |
| --- | --- | --- |
| 架构模式 | 分层架构（访问层/协调服务/数据节点/存储层） | 精简服务进程架构（可单机/集群） |
| 部署方式 | **Milvus Lite**（内嵌）  **Standalone**（Docker 单节点）  **Distributed**（K8s 分布式，支持水平扩展） | 本地二进制/Docker 部署  官方 Helm Chart 支持集群  支持商业版 Operator |
| 是否依赖外部组件 | Distributed 模式需 etcd/ZooKeeper | 无强依赖组件，部署更轻量 |
| 本地可用性 | 支持单节点上亿向量（Standalone）  高可用主从 | 单机即高可用，可动态扩容 |
| 适用场景 | 超大规模生产场景、企业级部署 | 中小规模项目、快速迭代环境 |

—

2. 资源占用与存储管理
------------

| 项目 | Milvus | Qdrant |
| --- | --- | --- |
| 向量压缩 | IVF\_PQ、IVF\_SQ8、HNSW\_PQ/SQ 支持压缩 | 支持 Scalar Quantization（INT8、Binary），最高节省 97% 内存 |
| 存储选项 | 支持 DiskANN、MMap 模式将索引/向量存于磁盘 | 支持 Memmap（内存映射），索引与数据可放入 SSD |
| GPU 加速 | 完善支持（CUDA/多GPU搜索） | 支持索引构建时 GPU，加速效果有限 |
| 内存需求 | 高性能索引需较大内存 | 内存占用灵活可控（通过量化/Memmap） |

—

3. 应用场景适配性
----------

| 场景 | Milvus 优势 | Qdrant 优势 |
| --- | --- | --- |
| 代码搜索 | 多索引类型支持大规模代码向量  支持元数据过滤 | JSON Payload 支持灵活元数据筛选  官方示例多，适合上手 |
| 客服问答（RAG） | 分布式支持大并发  支持 GPU 加速和高吞吐 | 多向量索引  Payload 属性过滤强 |
| 图像/视频搜索 | 图像识别、推荐广泛应用  多模态支持 | 图像搜索入门门槛低  元数据检索灵活 |
| 内部知识库检索 | 分区检索、布尔过滤支持强  大型文档案例丰富 | 支持字段筛选、轻量部署、快速集成 Haystack 等 |

—

4. 检索性能与索引机制
------------

| 项目 | Milvus | Qdrant |
| --- | --- | --- |
| 检索延迟 | P95 通常在数十～百毫秒（Standalone）  GPU 模式更低 | P95 延迟常低于 10ms（HNSW） |
| 并发吞吐 | 分布式可横向扩展  适合万级并发 | 单机高并发表现优异，吞吐领先 |
| 索引类型 | 支持 FLAT、IVF、HNSW、DiskANN、SCANN 等多种 | 自研 HNSW，支持量化优化 |
| 查询精度控制 | 精度-性能通过选择索引类型调节 | 通过 HNSW 参数 + 量化灵活调节 |
| 外存支持 | 支持 DiskANN + SSD 结构 | 支持 Memmap/SSD 索引映射 |

—

5. 数据更新与一致性管理
-------------

| 项目 | Milvus | Qdrant |
| --- | --- | --- |
| 增删改操作 | 支持 Upsert、布尔删除 | 支持 insert/update/delete  有 version 控制 |
| 实时一致性 | 分布式下可配置一致性等级（强/最终/会话） | WAL 日志机制保证最终一致性 |
| 索引更新 | HNSW 等支持在线插入  删除需重建索引恢复性能 | HNSW 支持更新，但建议定期 optimize |
| 删除机制 | 打标签后需重建索引 | Lazy deletion + 版本号控制，需手动 optimize |

—

6. 生态系统与集成支持
------------

| 项目 | Milvus | Qdrant |
| --- | --- | --- |
| SDK 语言 | Python、Go、Java、Node.js | Python、Go、Rust、Java、.NET、JS |
| 框架兼容 | LangChain、LlamaIndex、Haystack、OpenAI Embedding | 全面支持 LangChain、DocArray、Semantic Kernel |
| UI 工具 | 管理 UI + CLI 工具 | 自带 Web UI 可视化搜索 |
| 社区活跃度 | GitHub Star ~34.6k（2024）  企业应用广泛 | GitHub Star ~23.3k（2024）  示例项目多，易上手 |

—

7. 企业案例实践（简要）
-------------

| 项目 | 案例 |
| --- | --- |
| Milvus | AT&T（语义文档检索）、Walmart（商品推荐）、HumanSignal（LabelStudio 加速搜索） |
| Qdrant | Sprinklr（客服语义检索）、Tactiq（会议纪要匹配）、Heygen（视频语音搜索） |

—

总结建议
----

* 若你希望快速构建语义搜索或轻量级 RAG 系统，**Qdrant 更易部署、更节省资源**；
* 若你面对 TB 级数据、GPU 加速需求或企业生产场景，**Milvus 提供更多索引选择与分布式能力**；
* 二者均兼容主流嵌入模型与检索框架，推荐基于 PoC 快速对比部署效果进行选型。
