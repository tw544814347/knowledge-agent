# vector db & RAG

> **Page ID**: 2742657412
> **URL**: https://confluence.shopee.io/pages/viewpage.action?pageId=2742657412

[overvie](https://arxiv.org/pdf/2410.12837)[w paper](https://arxiv.org/pdf/2410.12837)
======================================================================================

vectordb向量数据库调研对比
=================

面向企业私有部署和LLM场景，常见的向量数据库方案包括 **pgvector**、**Infinity (InfiniFlow)**、**FAISS**、**Milvus**、**Qdrant**、**Weaviate**、**Pinecone**、**Chroma**、**Elasticsearch (ES)** 等。下表比较了它们的核心特性：

| 方案 | 适用场景 | 索引方式 | 查询速度 | 分布式支持 | 数据更新能力 | 生态兼容性 | 易用性 | 可扩展性 | 适合LLM场景 | 存储方式 | API兼容性 | 存储开销 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **pgvector** | 依托PostgreSQL的场景 | GiST/BRIN（默认）；可选HNSW/IVF[github.com](https://github.com/pgvector/pgvector#:~:text=By%20default%2C%20pgvector%20performs%20exact,search%2C%20which%20provides%20perfect%20recall) | 中等（需索引） | 无内建分布式（依赖PG集群） | 在线更新（SQL可直接插入更新） | PostgreSQL生态丰富 | 学习曲线低（SQL操作），但需扩展 | 取决于PostgreSQL集群 | 良好（集成方便） | 存于PG表中 | SQL/REST（Pg链接） | 较小（与PG表相同） |
| **Infinity** | AI原生检索，低延迟需求 | 自研（混合向量/关键词） | 极快（百万级0.1ms[infiniflow.org](https://infiniflow.org/#:~:text=Incredibly%20fast)、支持15K QPS） | 无（单实例） | 支持动态更新 | Python SDK直观，低依赖 | 易于上手（单可执行文件、直观API） | 单机效率极高，集群待开发 | 优秀（AI原生架构） | 自研存储 | Python API | 低（高效索引） |
| **FAISS** | 嵌入式近邻搜索（库，不是DB） | 支持Flat/IVF/HNSW/PQ等 | 极高（GPU加速千级QPS） | 无（单机/GPU） | 更新受限（部分索引需重建） | 广泛支持（Python/C++） | 编程友好（Python库），但需配置 | 单机高效（支持CPU/GPU多种索引） | 良好（常作后端索引引擎） | 内存+磁盘 | C++/Python API | 较高（内存敏感） |
| **Milvus** | 大规模AI检索 | 支持多种索引（IVF、HNSW、PQ等） | 高（专为大量数据优化） | 支持集群（可水平扩展）[milvus.io](https://milvus.io/#:~:text=Milvus%20is%20an%20open,vectors%20with%20minimal%20performance%20loss) | 在线更新（支持Upsert） | 云服务（Zilliz Cloud）、丰富插件 | 提供Python/REST，配置灵活 | 高（数十亿向量，集群架构）[milvus.io](https://milvus.io/#:~:text=Milvus%20is%20an%20open,vectors%20with%20minimal%20performance%20loss) | 优秀（专为GenAI设计） | 磁盘+内存（列式存储） | Python/REST | 中等（要存索引和向量） |
| **Qdrant** | 高性能向量检索，云原生 | HNSW | 高（Rust实现优化） | 支持（企业版多节点） | 在线更新（支持压缩和磁盘溢出） | Docker快速部署，Rust生态稳定 | 易用（Docker快速启动，REST API） | 支持水平扩展（自动弹性，零停机）[qdrant.tech](https://qdrant.tech/#:~:text=Cloud,downtime%20upgrades.%20Qdrant%20Cloud) | 优秀（设计用于RAG） | 内存+磁盘 | REST/GRPC | 中等（支持压缩） |
| **Weaviate** | AI搜索/知识图谱 | HNSW（向量）；BM25（关键词） | 高（混合查询） | 支持（多租户，K8s部署）[weaviate.io](https://weaviate.io/platform#:~:text=Get%20the%20best%20of%20vector,and%20keyword%20search) | 在线更新（增删改自动同步） | 提供GraphQL/API，集成ML模型 | 易用（自带UI和丰富配置） | 高（横向扩展，原生多租户）[weaviate.io](https://weaviate.io/platform#:~:text=Get%20the%20best%20of%20vector,and%20keyword%20search) | 优秀（混合检索，RAG直连） | 磁盘存储向量 | REST/GraphQL | 中等（支持压缩） |
| **Pinecone** | SaaS向量DB，大规模应用 | HNSW（专有） | 极高（专用基础设施） | 内建（全托管，支持扩展） | 在线更新（自动管理索引） | 与云服务紧密集成 | 无需维护（SaaS，开箱即用） | 高（云服务自动扩展） | 良好（生产级服务） | 云端存储 | REST | 可变（自动扩缩） |
| **Chroma** | AI应用数据库（文档+检索） | HNSW | 高（轻量级实现） | 部分（分布式计划中） | 在线更新（专为应用设计） | Python原生，融入多个开发框架 | 易用（Python库，All-in-One） | 一定（目前不分布式，仅单机） | 良好（适合开发环境） | 本地/磁盘 | Python/REST | 较小（轻量设计） |
| **Elasticsearch** | 通用搜索引擎+向量检索 | HNSW（7.17+），倒排索引 | 中等（并行分片，但索引体积大） | 支持（分布式集群） | 在线更新（文档型更新） | 全栈搜索生态（ELK等） | 复杂度中等（需要集群管理） | 高（企业级集群，海量数据） | 良好（向量+关键词混合检索） | 磁盘索引 | REST/Kibana API | 高（索引存储大） |

**优选方案：** 对于企业私有部署且需调用OpenAI API场景，推荐**Milvus、Weaviate、Qdrant、Infinity、Chroma、pgvector**等开源方案。这些方案均支持本地部署，易集成OpenAI嵌入（Embedding）和LLM服务。如Milvus可横向扩展[milvus.io](https://milvus.io/#:~:text=Milvus%20is%20an%20open,vectors%20with%20minimal%20performance%20loss)，Weaviate内置混合检索与RAG功能[weaviate.io](https://weaviate.io/platform#:~:text=Get%20the%20best%20of%20vector,and%20keyword%20search)，Infinity原生高性能[infiniflow.org](https://infiniflow.org/#:~:text=Incredibly%20fast)，而pgvector可直接在PostgreSQL环境下部署[github.com](https://github.com/pgvector/pgvector#:~:text=By%20default%2C%20pgvector%20performs%20exact,search%2C%20which%20provides%20perfect%20recall)。相对而言，Pinecone为SaaS（不支持私有化）而Elasticsearch检索速度与存储开销较大，不是首选。

rag检索增强生成（RAG）框架调研对比
====================

常见开源RAG框架及平台包括 **LangChain**、**LlamaIndex**、**Haystack**、**Flowise**、**Langflow**、**RAGFlow**、**FastGPT**、**Dify**、**LangChain-ChatChat**、**OpenDevin**、**ChatGPT-RAG** 等。

下表比较了它们的定位与特性，并注明“国产/国际”及“是否支持私有部署”：

| 框架 | 核心定位 | 文档处理能力 | 支持模型/Embedding | 检索优化能力 | 向量库兼容性 | 特色功能 | UI 界面 | 集成能力 | 部署方式 | 适用场景 | 社区活跃度 | 国/外 | 私有化部署 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **LangChain** | LLM应用开发框架、支撑RAG流水线[firecrawl.dev](https://www.firecrawl.dev/blog/best-open-source-rag-frameworks#:~:text=LangChain%20emerged%20as%20one%20of,augmented%20generation%20systems) | 支持多种文档加载器、分块策略 | OpenAI、Hugging Face 等 | 多策略检索（关键词+向量） | 通过接口兼容大多数向量DB | 链、Agent、记忆、LangGraph等 [firecrawl.dev](https://www.firecrawl.dev/blog/best-open-source-rag-frameworks#:~:text=LangChain%20emerged%20as%20one%20of,augmented%20generation%20systems) | 无（代码库） | 支持多模型、多服务、插件丰富 | 代码库 (pip) | 通用LLM应用、RAG | 极高 (105k★)[firecrawl.dev](https://www.firecrawl.dev/blog/best-open-source-rag-frameworks#:~:text=LangChain%20emerged%20as%20one%20of,augmented%20generation%20systems) | 国外 | 支持 |
| **LlamaIndex** | 企业知识助手框架[docs.aperturedata.io](https://docs.aperturedata.io/Integrations/llamaindex_howto#:~:text=LlamaIndex%20is%20a%20simple%2C%20flexible,Augmented%20Generation) | 强大的文档解析、索引流水线 | 多种LLM及Embedding | 支持分层检索、知识图谱 | 支持ApertureDB、Chroma等向量存储 | Workflow机制、图数据库查询[docs.aperturedata.io](https://docs.aperturedata.io/Integrations/llamaindex_howto#:~:text=LlamaIndex%20is%20a%20simple%2C%20flexible,Augmented%20Generation) | 无（代码库） | 与LangChain等集成，企业级功能 | 代码库 (pip) | 知识管理、上下文问答 | 较活跃 (40k★+) | 国外 | 支持 |
| **Haystack** | 端到端RAG管道开发平台 | 支持PDF、文本、音频等多模态 | Transformer模型等 | 支持混合检索（BM25+ANN） | 支持Elasticsearch/FAISS等常见存储 | 可视化Pipeline(Studio)，自校正循环[haystack.deepset.ai](https://haystack.deepset.ai/#:~:text=RAG) | 有 (Deepset Studio) | 集成多种Embedding模型、工具 | 代码库 (pip) | 企业搜索、QA、对话 | 活跃 (GitHub活跃) | 国外 | 支持 |
| **Flowise** | 低代码LLM应用编排工具 | 可接入多种数据源 | Any (通过LangChain) | 通过节点可定制检索策略 | 兼容Chroma、FAISS等（由LangChain管理） | 节点式可视化流程，集成记忆与缓存[flowiseai.com](https://flowiseai.com/#:~:text=LLM%20Orchestration) | 有 (可视化节点) | 内置100+集成（LangChain、LlamaIndex等）[flowiseai.com](https://flowiseai.com/#:~:text=LLM%20Orchestration) | 桌面/容器 (npm) | 业务流程自动化、对话助手 | 中等 (1.8w★) | 国外 | 支持 |
| **Langflow** | 可视化AI Agent/RAG构建工具 | 可接入文本、文档 | Any (通过LangChain) | 可视化设计检索流程 | 兼容多种向量DB（LangChain底层） | 低代码界面，支持任意API/模型[langflow.org](https://www.langflow.org/#:~:text=Langflow%20is%20a%20low,any%20API%2C%20model%2C%20or%20database) | 有 (可视化节点) | 支持任意LLM及工具链 | 桌面/容器 | Agent、RAG应用 | 活跃 (12k★) | 国外 | 支持 |
| **RAGFlow** | 深度文档理解的RAG引擎[github.com](https://github.com/infiniflow/ragflow#:~:text=RAGFlow%20is%20an%20open,from%20various%20complex%20formatted%20data) | 强化文档结构化解析（表格、布局等） | 支持OpenAI及私有模型 | 知识图谱、关键字扩展 | 默认Elasticsearch（也支持Infinity）[github.com](https://github.com/infiniflow/ragflow#:~:text=RAGFlow%20uses%20Elasticsearch%20by%20default,to%20Infinity%2C%20follow%20these%20steps) | 端到端引用标注问答，高级文档处理[github.com](https://github.com/infiniflow/ragflow#:~:text=RAGFlow%20is%20an%20open,from%20various%20complex%20formatted%20data) | 无（代码库） | 数据预处理、检索、图谱结合 | 容器部署 | 企业级知识问答 | 较活跃 (48k★) | 国产 | 支持 |
| **FastGPT** | 开源知识库平台，面向企业QA | 自动化预处理、多格式支持 | 多种LLM | 内置RAG检索 | 可能内嵌向量存储（未公开细节） | 可视化工作流，Slack/Discord集成[tryfastgpt.ai](https://tryfastgpt.ai/#:~:text=EmpowerImage%3A%20logowith%20Your%20Expertise) | 有 (Web UI) | 多模型兼容、API友好（OpenAI对齐）[tryfastgpt.ai](https://tryfastgpt.ai/#:~:text=Seamlessly%20connect%20with%20existing%20GPT,aligned%20APIs)[tryfastgpt.ai](https://tryfastgpt.ai/#:~:text=Multi) | 容器部署 | 行业知识库、问答 | 活跃 (1.8w★) | 国产 | 支持 |
| **Dify** | LLM应用开发平台，内置RAG引擎[dify.ai](https://dify.ai/#:~:text=The%20Innovation%20Engine%20for%20GenAI,Applications) | 支持PDF、PPT等文档 | 多模型 | 端到端RAG流水线 | 支持多种后端存储 | 可视化流程、插件市场、LLMOps[dify.ai](https://dify.ai/#:~:text=The%20Innovation%20Engine%20for%20GenAI,Applications) | 有 (Orchestration Studio) | 插件式集成（50+工具、SSO等） | 容器/云部署 | 企业级AI应用 | 活跃 (90k★) | 国产 | 支持 |
| **LangChain-ChatChat** | 基于LangChain和国产模型的RAG/Agent应用 | 文档检索和多轮对话支持 | ChatGLM、Qwen、Llama等 | 多轮对话+检索 | 支持常见向量DB（LangChain接口） | 本地化离线部署、结合国产大模型[github.com](https://github.com/chatchat-space/Langchain-Chatchat#:~:text=Langchain,and%20Agent%20app%20with%20langchain)[github.com](https://github.com/chatchat-space/Langchain-Chatchat#:~:text=%E5%9F%BA%E4%BA%8E%20ChatGLM%20%E7%AD%89%E5%A4%A7%E8%AF%AD%E8%A8%80%E6%A8%A1%E5%9E%8B%E4%B8%8E%20Langchain%20%E7%AD%89%E5%BA%94%E7%94%A8%E6%A1%86%E6%9E%B6%E5%AE%9E%E7%8E%B0%EF%BC%8C%E5%BC%80%E6%BA%90%E3%80%81%E5%8F%AF%E7%A6%BB%E7%BA%BF%E9%83%A8%E7%BD%B2%E7%9A%84,RAG%20%E4%B8%8E%20Agent%20%E5%BA%94%E7%94%A8%E9%A1%B9%E7%9B%AE%E3%80%82) | 有 (简单界面) | 集成本地模型及工具 | 桌面/容器 | 中文RAG问答 | 非常活跃 (34k★) | 国产 | 支持 |
| **OpenDevin** | 自主AI软件工程师（代码开发Agent） | 非RAG（代码语料、任务描述） | GPT-4、ChatGPT、开源模型 | 概念检索 | 不适用 | 场景驱动的Agent（shell、浏览器）[github.com](https://github.com/AI-App/OpenDevin.OpenDevin#:~:text=Welcome%20to%20OpenDevin%2C%20an%20open,source%20community) | 有 (Chat界面) | 专注软件开发工具链 | 容器/自部署 | 自动编程助手 | 适中 | 国产 | 支持 |
| **ChatGPT-RAG** | 基于ChatGPT的检索增强生成方案（Demo性质） | 依赖外部检索系统 | GPT-4（OpenAI） | 用户自建向量搜索 | 与任意向量存储结合（用户选择） | 无编排，只是示例应用 | 无（调用API） | 通过API调用检索结果后构造提示 | 云端（OpenAI API） | 基础问答、对话 | 使用极广 | 国外 | 不支持 |

以上对比中，**国产方案**（标注“国产”）包括RAGFlow、FastGPT、Dify、LangChain-ChatChat、OpenDevin等，均支持私有化部署。**国际方案**（标注“国外”）如LangChain、Haystack等也完全可本地部署。支持可视化界面的框架（如Haystack Studio、Flowise、Langflow、Dify）更易于快速搭建RAG应用，而轻量级代码库（如LangChain、LlamaIndex、RAGFlow）适合工程团队集成开发。

架构设计方案
======

**整体架构：** 下图展示了企业私有化部署的RAG系统架构示意。用户请求首先由应用层接收，并由**检索模块**触发对本地知识库的查询。文档数据经过预处理（OCR、分词、分块）后被**嵌入模型**（如OpenAI Embedding、BGE）转换为向量，存储于**向量数据库**（Milvus、Weaviate、Qdrant等）。当用户提问时，系统将查询转换为向量，在向量库中检索Top-K相关文档，将这些文档连同原始问题拼接为**增强提示**（Prompt with Context），再交给**生成模型**（如OpenAI GPT-4、国产大模型BGE等）生成答案。最终结果会与参考文档链接一起反馈给用户，以提升回答准确性和可追溯性。

 

**组件流程：** 系统可分为数据预处理、索引存储、检索查询、生成回答四大环节。文档入库时，预处理服务使用OCR/VLLM解析图像和复杂格式，文本分片后调用Embedding API（OpenAI或本地模型）生成向量，并插入向量数据库（步骤1-3）。运行时（步骤4-6），用户在前端输入问题，RAG框架（如Dify或Haystack）将通过向量检索器查询相关文档并优化检索（可加入关键字过滤、多模态检索等）。检索结果被打包进提示，调用LLM生成回答（步骤7-8）。整个流程在私有网络内完成，不依赖外部云服务。

 ![Retrieval-Augmented%20Generation.png](https://www.k2view.com/hs-fs/hubfs/Retrieval-Augmented%20Generation.png?width=700&height=340&name=Retrieval-Augmented%20Generation.png)

*RAG系统架构示意：用户查询在向量数据库检索相关内容，再由LLM生成回答，适用于企业私有部署（改自参考[k2view.com](https://www.k2view.com/what-is-retrieval-augmented-generation#:~:text=RAG%20architecture)[zilliz.com](https://zilliz.com/blog/safeguard-data-integrity-on-prem-rag-deployment-with-llmware-and-milvus#:~:text=9,the%20LLM%20is%20Bling%207B)）。*

 

**典型使用案例：**

* **AI研发助手：** 为研发人员提供代码文档、技术方案的快速检索与解答。系统接入公司知识库、技术文档、知识图谱等，结合Code LLM（如ChatGPT或BGE），实时回答设计方案、接口使用、异常排查等问题。该场景中向量库可为Milvus或Qdrant，RAG框架选用支持函数调用的LangChain或FastGPT，提供代码片段和引用来源，使研发工作更高效。
* **智能问答平台：** 面向客服和内外部用户，提供文档驱动的自然语言问答。系统集成企业文档库、FAQ、CRM数据等，使用检索增强生成技术降低LLM幻觉率。部署如Haystack或Dify建立多轮对话Bot，结合ChatGPT API执行对话生成，并将检索到的知识段插入提示。此外，可引入语音识别模块，实现**多模态问答**（参考图像和文字共同检索）[github.com](https://github.com/infiniflow/ragflow#:~:text=Latest%20Updates)。

**行业落地示例：**

* **金融行业：** 银行知识库或风控法规文档量大且更新频繁。可构建**智能合规助手**：将最新监管文件和交易记录嵌入向量库，用户（如风控人员）提问时系统检索相关法规条款并由LLM生成解释。例如Zilliz提出在金融场景下需私有化部署RAG[zilliz.com](https://zilliz.com/blog/safeguard-data-integrity-on-prem-rag-deployment-with-llmware-and-milvus#:~:text=services,financial%20and%20legal%20services%20companies)[zilliz.com](https://zilliz.com/blog/safeguard-data-integrity-on-prem-rag-deployment-with-llmware-and-milvus#:~:text=This%20architecture%20diagram%20illustrates%20RAG%27s,premises%20using%20LLMware%20and%20Milvus)，以确保数据安全。此场景可使用Milvus+RAGFlow组合，高效处理复杂文档结构并满足合规要求。
* **制造业：** 工程手册、维修记录和物料规范分散在多个系统中。可部署**智能运维助手**：接入生产知识库、故障报告和设备数据，RAG系统快速定位解决方案。使用向量检索找到历史故障描述，由LLM提供维修指导。如利用Weaviate的向量搜索和过滤功能进行知识检索[weaviate.io](https://weaviate.io/platform#:~:text=Get%20the%20best%20of%20vector,and%20keyword%20search)，并结合LangChain-ChatChat实现全中文的本地部署。
* **内容平台：** 媒体或知识付费平台有海量文章、视频字幕等非结构化内容。可建立**智能内容推荐/问答系统**：用户提问时先检索相关文章摘要，再由LLM整合信息。方案可采用Chroma或pgvector等轻量级存储视频/文章的向量，结合Flowise可视化构建复杂的推荐与问答流程，提高用户粘性。

以上组件互相协同：**嵌入模型**生成语义向量，**向量库**高效检索，**RAG框架**负责编排检索与生成流程，[github.com](https://github.com/infiniflow/ragflow#:~:text=RAGFlow%20is%20an%20open,from%20various%20complex%20formatted%20data)所示的RAGFlow即是此类架构的实例，专注深度文档理解并提供可替换的检索后端[github.com](https://github.com/infiniflow/ragflow#:~:text=RAGFlow%20uses%20Elasticsearch%20by%20default,to%20Infinity%2C%20follow%20these%20steps)。企业可根据需求选型，例如以对中文支持更好的LangChain-ChatChat或LlamaIndex作为框架，以OpenAI API或BGE等LLM作为生成核心。

 

**参考资料：** 最新文档与业界报告（包括2024年后发布的官方文档、GitHub项目、论文等）均被用于分析与决策，例如Milvus对大规模向量检索的说明[milvus.io](https://milvus.io/#:~:text=Milvus%20is%20an%20open,vectors%20with%20minimal%20performance%20loss)、Qdrant对云原生可扩展性的描述[qdrant.tech](https://qdrant.tech/#:~:text=Cloud,downtime%20upgrades.%20Qdrant%20Cloud)、LangChain和Dify等框架的功能对比[firecrawl.dev](https://www.firecrawl.dev/blog/best-open-source-rag-frameworks#:~:text=LangChain%20emerged%20as%20one%20of,augmented%20generation%20systems)[firecrawl.dev](https://www.firecrawl.dev/blog/best-open-source-rag-frameworks#:~:text=Dify%20is%20an%20open,ready%20AI%20applications)等。上述汇报结构清晰、图表并举，适合高层决策者了解技术选型。
