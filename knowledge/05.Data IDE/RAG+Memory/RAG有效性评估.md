# RAG有效性评估

> **Page ID**: 2749040235
> **URL**: https://confluence.shopee.io/pages/viewpage.action?pageId=2749040235

评估RAG（Retrieval Augmented Generation）系统的有效性是一个多方面的问题，需要结合信息检索（IR）和自然语言生成（NLG）的评估方法，并关注两者如何协同工作。

一、核心评估维度
--------

一个有效的RAG系统应该在以下几个核心维度上表现良好：

1. **检索质量 (Retrieval Quality):** RAG系统的第一步是检索。如果检索到的上下文不相关或不准确，后续的生成质量也无从谈起。
   1. **上下文相关性/精确度 (Context Relevance / Context Precision):** 检索到的文档/文本块与用户查询的相关程度如何？
   2. **上下文召回率 (Context Recall):** 检索系统是否能够找到知识库中所有与查询相关的文档/文本块？
   3. **上下文充分性 (Context Sufficiency):** 检索到的上下文是否包含足够的信息来回答用户的问题？

1. **生成质量 (Generation Quality):** 在给定检索到的上下文后，LLM生成的答案质量如何？
   1. **忠实性/可归因性/有据性 (Faithfulness / Attributability / Groundedness):** 生成的答案是否严格基于提供的上下文？是否避免了基于上下文的幻觉？答案中的声明是否可以明确追溯到检索到的特定文本块？
   2. **答案相关性/有用性 (Answer Relevance / Helpfulness):** 生成的答案是否直接、清晰地回答了用户的问题，并且对用户有实际帮助？
   3. **答案准确性 (Answer Correctness):** 生成的答案在事实上是否正确（这可能超出上下文的范围，但对于用户来说很重要）。
   4. **流畅性/连贯性 (Fluency / Coherence):** 生成的答案是否自然、易于理解？

1. **端到端性能 (End-to-End Performance):** 综合考量检索和生成的效果。
   1. **最终答案的正确性和相关性:** 系统作为一个整体，其最终输出的答案是否正确且与用户意图相关。
   2. **用户满意度:** 用户对系统整体表现的满意程度。

1. **其他重要因素：**
   1. **延迟 (Latency):** 从用户提问到获得答案所需的时间。
   2. **成本 (Cost):** API调用、计算资源、存储等成本。
   3. **鲁棒性 (Robustness):** 系统在面对不同类型查询、噪声输入或知识库变化时的稳定性。
   4. **可扩展性 (Scalability):** 系统处理不断增长的数据量和用户请求的能力。

二、理论依据
------

* **信息检索 (Information Retrieval - IR):** 传统IR领域的评估指标为检索质量提供了理论基础。
* **自然语言处理/生成 (NLP/NLG):** NLG评估方法用于衡量生成文本的质量，但传统的NLG指标（如BLEU, ROUGE）主要关注文本相似性，对于RAG的忠实性和事实性评估能力有限。
* **事实性与知识基础评估 (Factuality and Knowledge Grounding):** 这是当前LLM评估研究的热点，旨在衡量模型输出是否基于给定知识源且事实正确。

三、评估标准与具体指标
-----------

### 1. 检索质量指标 (Retrieval Metrics)

* **Precision@k:** 检索到的前k个结果中相关的比例。
* **Recall@k:** 检索到的前k个结果中包含的相关文档占所有相关文档的比例。
* **Mean Reciprocal Rank (MRR):** 第一个相关结果排名的倒数的平均值。关注找到第一个正确答案的速度。
* **Normalized Discounted Cumulative Gain (nDCG@k):** 考虑了相关性等级和排名位置，更细致地评估排名质量。
* **Hit Rate:** 至少检索到一个相关文档的查询比例。
* **Context Precision (RAGAS):** 评估检索到的上下文中与问题相关的句子的比例。（使用LLM判断）
* **Context Recall (RAGAS):** 评估答案中的每个句子是否都能在检索到的上下文中找到对应的句子。（使用LLM判断）

### 2. 生成质量指标 (Generation Metrics)

* **Faithfulness (RAGAS, TruLens):** 衡量生成的答案在多大程度上基于检索到的上下文。通常通过LLM判断答案中的每个声明是否能被上下文所支持。
* **Answer Relevancy (RAGAS):** 衡量生成的答案与原始问题的相关性。（使用LLM判断）
* **Answer Semantic Similarity (RAGAS):** 衡量生成的答案与真实答案/理想答案之间的语义相似度。
* **Answer Correctness (RAGAS):** 衡量生成的答案与真实答案/理想答案在事实准确性上的一致性。（使用LLM判断）
* **Groundedness (TruLens):** 评估答案中有多少部分是可以被提供的上下文所支持的。
* **人工评估:**
  + **Likert 打分 (例如1-5分):** 针对忠实性、相关性、清晰度、有用性等维度进行人工打分。
  + **错误分析 (Error Analysis):** 对不理想的答案进行归类（如：事实错误、上下文外推、不相关、不流畅等）。

### 3. 端到端指标 (End-to-End Metrics)

* 通常是上述检索和生成指标的组合，或者通过人工评估直接衡量最终答案的质量。
* **任务完成率 (Task Completion Rate):** 如果RAG用于特定任务（如回答特定类型的技术问题），评估任务成功完成的比例。
* **用户反馈:** 例如点赞/点踩、用户评论、会话时长等。

四、评估框架与工具
---------

* **[RAGAS](https://github.com/explodinggradients/ragas) (Retrieval-Augmented Generation Assessment):**
  + 一个流行的开源Python库，提供了一套评估RAG管道的指标，如 faithfulness, answer\_relevancy, context\_recall, context\_precision 等。它通常利用LLM本身来进行部分指标的自动化评估。
  + **优点:** 自动化程度高，提供多种关键指标。
  + **缺点:** 依赖LLM作为评估者，可能引入评估偏差；部分指标需要标准答案。
* **[TruLens](https://github.com/truera/trulens):**
  + 提供LLM应用可观察性和评估的工具，特别强调"Triad"评估（Groundedness, Relevance, Helpfulness）。可以跟踪中间结果，帮助调试。
  + **优点:** 深入的可观察性，支持多种评估维度。
* **[DeepEval](https://github.com/confident-ai/deepeval):**
  + 另一个单元测试和评估LLM应用的框架，支持自定义指标和真实性评估。
* **[ARES](https://github.com/stanford-futuredata/ARES) (Automated RAG Evaluation System):**
  + 一种通过生成合成查询和预测人类偏好来自动化RAG评估的方法。
* **LangSmith (来自Langchain):**
  + 提供LLM应用的全生命周期管理，包括日志、追踪、调试和评估。可以用于收集和分析RAG系统的运行数据，并进行人工标注和评估。

五、实际操作步骤与建议
-----------

1. **构建评估数据集 (Golden Dataset):**
   1. **问题集 (Questions):** 收集代表性的用户查询。对于公司内部研发RAG，这些问题应该覆盖研发日常工作中可能遇到的各类技术问题、规范查询等。
   2. **理想上下文 (Ground Truth Context):** 对于每个问题，人工标注出知识库中哪些文档/文本块是回答该问题的理想上下文。
   3. **标准答案 (Ground Truth Answers):** 对于每个问题（和理想上下文），撰写一个或多个高质量的参考答案。
   4. 这个数据集是进行精确评估的基础，虽然构建成本高，但价值巨大。
2. **选择合适的指标:** 根据评估目标选择最重要的指标。例如，对于研发辅助，答案的 Faithfulness 和 Answer Correctness 可能比 Fluency 更重要。
3. **结合自动化与人工评估:**
   1. 使用RAGAS等工具进行快速、大规模的自动化评估，获取基线数据。
   2. 对自动化评估结果进行抽样，并进行深入的人工评估，以验证自动化指标的可靠性，并发现自动化评估无法捕捉的细微问题。
4. **进行A/B测试:** 当比较不同的RAG配置（如不同的分块策略、嵌入模型、检索器、LLM或提示）时，A/B测试是非常有效的方法。
5. **关注失败案例 (Failure Case Analysis):** 深入分析系统表现不佳的案例，理解是检索阶段出了问题，还是生成阶段出了问题，或者是两者皆有。
6. **迭代优化:** 评估不是一次性的，而是一个持续的过程。根据评估结果不断迭代优化RAG系统的各个组件。
7. **考虑特定场景:** 公司内部研发RAG的评估可能还需要考虑：
   1. **代码相关查询的特殊性:** 是否能准确检索和理解代码片段？
   2. **内部术语和规范的覆盖度:** 是否能正确理解和使用公司内部的技术术语和开发规范？
   3. **知识更新的及时性:** 当内部文档更新后，RAG系统是否能及时反映这些更新？

通过上述维度、指标和方法的结合，可以对RAG系统的有效性进行全面且深入的评估，从而指导其优化和改进。
