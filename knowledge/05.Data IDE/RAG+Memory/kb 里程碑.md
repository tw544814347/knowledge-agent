# kb 里程碑

> **Page ID**: 2829606930
> **URL**: https://confluence.shopee.io/pages/viewpage.action?pageId=2829606930

KB里程碑(2025)
===========

| 里程碑 | 时间点 | 主要功能 | 备注 |
| --- | --- | --- | --- |
| V0.1 | 20250707 | * ~~支持本地文档上传（pdf / docs / markdown / json / csv等格式）~~ * ~~支持confluence文档导入，支持按照文档目录层级结构批量导入。~~ * ~~支持选定chunk策略（默认auto自动根据文档类型路由）~~ * ~~支持基于知识库的RAG对话验证效果。~~ |  |
| V0.2 | 20250729 | * ~~支持confluence文档中图片提取~~ * ~~支持图片理解，抽取关键信息+summary（使用vision LLM）~~ * ~~支持知识图谱相关信息抽取（实体+实体关系）~~ |  |
| V0.3 | 20250812 | * 支持将文档按照不同collection进行导入（导入筛选，查询过滤） * 支持选定特定策略rechunk * 支持检索结果citation | 20250808   1. 添加不同知识库collection（knowledge\_base\_id）支持 2. 支持reprocess功能，可选择不同的chunk strategy进行重新分chunk处理 3. 支持S3作为原始文档存储 4. 支持chunk-comparison，可视化对输入文本内容进行不同chunk strategy效果对比 |
| V0.4 | 20250826 | * 支持LLM进行chunk * 支持LLM进行实体识别与抽取 * 支持Milvus引擎 |  |
| V0.5 | 20250909 | * 支持confluence元数据抽取 * 已有chunk策略调优 * 支持告警信息导入，效果验证 |  |
| V0.6 | 20250923 | * 支持MySQL引擎（替代现有PostgreSQL引擎） * 申请线上Milvus，MySQL，DNS，space等，标准化准备 * KMS相关改造 * Test环境发布验证 |  |
| V1.0 | 20251007 | * Live发布第一版 | +业务接入使用，反馈review |
| V1.1 | 20251021 | * 文档质量校验方案TD * 文档质量提升方案TD |  |
| V1.2 | 20251104 | * 文档质量校验+提升Dev |  |
| V1.3 | 20251118 | * 文档标注调研（LabelStudio） * 文档标注TD |  |
| V1.4 | 20251202 | * 文档标注Dev |  |
| V1.5 | 20251216 | * 知识库质量评估方案调研 * 知识库质量评估TD |  |
| V1.6 | 20251230 | * 知识库质量评估Dev |  |
