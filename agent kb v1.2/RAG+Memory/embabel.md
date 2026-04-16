---
topic: agent-framework
relevance: core
language: mixed
source: confluence
last_reviewed: 2026-04-16
---

# embabel

> **Page ID**: 2897707783
> **URL**: https://confluence.shopee.io/pages/viewpage.action?pageId=2897707783

设计一个通用的 Agent 间数据转换方案，并提出了关于 `@Tool` 方法参数、AI 在 Tool 内部调用、`@Action` 的 `toolGroups` 组合使用、Tool 错误处理以及架构兼容性的问题。
### 1. Tool 方法参数类型
`@Tool` 方法可以接受 `Object` 类型参数，但需要注意其在 LLM 调用时的序列化和反序列化行为。Embabel 框架通过 `@Tool` 注解支持将方法暴露给 LLM 使用 。当您在 `@Tool` 方法中使用 `Object` 类型时，LLM 实际接收到的是该 `Object` 的 JSON 序列化形式。因此，您需要确保 `Object` 及其内部的 `Class<T>` 参数能够被正确地序列化和反序列化，并且 LLM 能够理解这些类型。
例如，在 `embabel-agent-api/src/test/kotlin/com/embabel/agent/api/annotation/support/testTypes.kt` 中，`PersonWithReverseTool` 类包含一个 `@Tool` 方法 `reverse()`，它操作的是 `PersonWithReverseTool` 自身的 `name` 属性 。虽然这里没有直接使用 `Object` 类型，但它展示了 `@Tool` 方法如何处理其所在类的实例数据。
### 2. AI 在 Tool 内部调用
在 `@Tool` 方法内部可以使用 AI 进行复杂的数据转换 。您可以通过 `AgentProcess.get()` 获取当前的 `AgentProcess` 实例，进而访问 `OperationContext` 来调用 AI 服务 。
例如，`Combined` 类中的 `toPersonWithPrompt` 方法展示了如何在 `@Action` 方法内部通过 `OperationContext` 调用 AI 服务 。虽然这是一个 `@Action` 方法，但同样的 `OperationContext` 机制也适用于 `@Tool` 方法，因为 `OperationContext` 提供了对 `PromptRunner` 的访问，而 `PromptRunner` 是进行 LLM 调用的接口 。
关于性能和调用方式的限制：
\* \*\*性能\*\*: 每次 AI 调用都会涉及与 LLM 的交互，这会引入网络延迟和计算成本。频繁或复杂的 AI 调用可能会影响 Tool 方法的执行效率。
\* \*\*调用方式\*\*: 您可以通过 `context.ai().withLlm(...)` 或 `context.ai().withDefaultLlm()` 获取 `PromptRunner`，然后使用 `createObject` 或 `generateText` 等方法进行 LLM 调用 。
### 3. ToolGroup 组合使用
一个 `@Action` 可以同时使用多个 `toolGroups` 。在 `@Action` 注解中，`toolGroups` 参数接受一个字符串数组，您可以列出所有需要的工具组。
例如，`findNewsStories` 方法在 `@Action` 注解中同时指定了 `CoreToolGroups.WEB` 和 `CoreToolGroups.BROWSER\_AUTOMATION` 两个工具组 。这表明该 Action 在执行时需要同时具备网页搜索和浏览器自动化能力。
### 4. Tool 错误处理
当 Tool 调用失败时，Embabel 框架的错误处理机制通常依赖于 `PromptRunner` 的行为和 Action 的设计。
\* \*\*`createObjectIfPossible`\*\*: `PromptRunner` 提供了 `createObjectIfPossible` 方法，它会在无法创建对象时返回 `null` 。这允许 Action 方法在 Tool 调用失败时进行优雅降级或触发重新规划。
\* \*\*Action 内部处理\*\*: 您可以在 `@Action` 方法内部使用标准的 Java/Kotlin 异常处理机制（`try-catch`）来捕获 Tool 调用或 AI 调用中可能发生的异常。
\* \*\*重新规划\*\*: 如果 `createObjectIfPossible` 返回 `null`，或者 Action 内部抛出未捕获的异常，Embabel 的 GOAP (Goal-Oriented Action Planning) 引擎可能会尝试重新规划，寻找其他路径来达成目标 。
目前的代码库中没有直接展示 `@Tool` 方法内部的错误处理模式，但 `@Action` 方法中的 AI 调用失败可以通过 `createObjectIfPossible` 来处理 。
### 5. 架构兼容性
这种“Agent 内部智能选择是否调用 Transform Tools”的模式是符合 Embabel 设计理念的，并且不会影响 GOAP 的规划效果 。
\* \*\*符合设计理念\*\*: Embabel 旨在通过声明式的方式（如 `@Action` 和 `toolGroups`）让开发者定义 Agent 的能力，而框架负责动态规划和执行 。将数据转换逻辑封装在 Tool 中，并在 Action 中声明对这些 Tool 的需求，正是这种理念的体现。`OperationContext` 允许 Action 灵活地访问 AI 和其他服务，从而实现智能选择和调用 。
\* \*\*不影响 GOAP 规划效果\*\*: GOAP 规划器根据 Action 的输入、输出和 `toolGroups` 等元数据来构建执行计划 。只要您在 `@Action` 中正确声明了所需的 `toolGroups`，规划器就会知道该 Action 需要哪些工具，并将其纳入规划考量。Tool 内部的复杂逻辑（包括 AI 调用）对于规划器来说是透明的，规划器只关心 Tool 是否能提供所需的功能。
您的目标是让所有 Agent 都能智能地消费其他 Agent 的结果，而不需要为每种组合创建专门的 bridge Agent。Embabel 通过 `Transformation` 接口和 `asTransformation` 函数支持将一个 Agent 封装为另一个 Agent 的 Action，从而实现 Agent 间的组合和数据转换 。这种机制允许您将一个 Agent 的输出作为另一个 Agent 的输入，而无需手动创建中间的 bridge Agent。
### Notes
`@Tool` 注解通常用于将方法暴露给 LLM，使其能够作为工具被调用 。`@Action` 注解则用于定义 Agent 的可执行操作，这些操作是 GOAP 规划的基本单位 。虽然两者都涉及方法执行，但它们在 Agent 框架中的角色和上下文不同。您提出的 `universalTransform` 方法更像是 `@Action` 的职责，因为它涉及复杂的 AI 驱动转换逻辑，并且可能作为 Agent 规划的一部分。如果将其定义为 `@Tool`，则意味着它是一个可以被 LLM 直接调用的外部功能，而不是 Agent 内部规划的步骤。
`DefaultActionMethodManager` 负责解析 `@Action` 方法的参数和工具组需求 。`AgentMetadataReader` 负责发现和处理 `@Agent`、`@Action` 等注解，并构建 Agent 的元数据 。这些组件共同确保了 Agent 行为的正确解析和执行。
Wiki pages you might want to explore:
- [Annotation-Based Agent Definition (embabel/embabel-agent)](/wiki/embabel/embabel-agent#5.1)
View this search on DeepWiki: https://deepwiki.com/search/agent-1-tooltoolobject-java-to\_8c6bd498-f418-42d8-a1a0-1e4aa808e9b8
