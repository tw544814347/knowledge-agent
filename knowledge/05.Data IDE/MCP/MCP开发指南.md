# MCP开发指南

> 来源: https://confluence.shopee.io/pages/viewpage.action?pageId=3120706887
> Space: FSDT (Financial Services Data Team)

## 1. MCP 是什么

**Model Context Protocol（MCP）** 是 Anthropic 于 2024 年发布的开放协议，旨在标准化 LLM 应用与外部数据源、工具之间的通信方式。可以把它理解为 AI 世界的 USB 接口——任何 MCP 客户端（Claude Desktop、Cursor、OpenAI 兼容客户端等）都能连接任何 MCP Server，无需为每个工具单独定制集成。

```
┌─────────────────┐         MCP 协议         ┌─────────────────────┐
│   MCP Client    │ ◄─────────────────────► │    MCP Server       │
│ (Claude/Cursor) │    JSON-RPC over HTTP    │  (你开发的服务)      │
└─────────────────┘                          └─────────────────────┘
```

### MCP 解决了什么问题

* **统一接口**：消除 LLM 集成各类工具时的重复适配工作。
* **安全边界**：工具的执行逻辑在 Server 端，客户端只接收结构化结果。
* **生态共享**：同一个 MCP Server 可被所有兼容客户端复用。

---

## 2. 核心概念

MCP Server 可以对外暴露三类能力：

| 概念 | 类比 | 作用 |
| --- | --- | --- |
| **Tools** | 函数/API | 模型可以主动"调用"执行具体操作，如查询数据库、截图、发邮件 |
| **Resources** | 只读文件/URL | 为模型提供上下文数据，如配置文件、知识库内容 |
| **Prompts** | Prompt 模板 | 预定义可复用的对话模板，减少重复提示词编写 |

### 交互流程

```
Client                          Server
  │                               │
  │── initialize ───────────────► │  握手，协商协议版本与能力
  │◄─ initialize result ──────── │
  │                               │
  │── tools/list ───────────────► │  获取可用工具列表
  │◄─ tools/list result ──────── │
  │                               │
  │── tools/call ───────────────► │  调用具体工具
  │◄─ tools/call result ──────── │
  │                               │
  │── session/delete ───────────► │  关闭会话（可选）
```

---

## 3. JSON-RPC 协议格式

MCP 使用 **JSON-RPC 2.0** 作为消息格式，所有客户端与服务端之间的交互都通过以下几种消息类型完成。

### 请求（Request）

客户端向服务端发送请求，服务端必须响应：

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "add",
    "arguments": { "a": 3, "b": 5 }
  }
}
```

| 字段 | 必须 | 说明 |
| --- | --- | --- |
| `jsonrpc` | 是 | 固定值 `"2.0"` |
| `id` | 是 | 整数或字符串，用于匹配响应；通知（Notification）不含此字段 |
| `method` | 是 | MCP 规范定义的方法名 |
| `params` | 否 | 参数对象，具体结构由 `method` 决定 |

### 成功响应（Response）

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "content": [{ "type": "text", "text": "8" }]
  }
}
```

### 错误响应（Error Response）

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "error": {
    "code": -32601,
    "message": "Method not found",
    "data": { "method": "tools/unknown" }
  }
}
```

常见标准错误码：

| 错误码 | 含义 |
| --- | --- |
| `-32700` | Parse error（JSON 解析失败） |
| `-32600` | Invalid Request（非法请求结构） |
| `-32601` | Method not found（方法不存在） |
| `-32602` | Invalid params（参数错误） |
| `-32603` | Internal error（服务内部错误） |

### MCP 定义的所有方法

**生命周期：**

| 方法 | 方向 | 说明 |
| --- | --- | --- |
| `initialize` | Client → Server | 握手，协商版本与能力 |
| `notifications/initialized` | Client → Server | 客户端初始化完成通知 |
| `ping` | 双向 | 心跳检测 |
| `session/terminate` | Client → Server | 显式关闭 Session |

**Tools：**

| 方法 | 说明 |
| --- | --- |
| `tools/list` | 获取工具列表 |
| `tools/call` | 调用指定工具 |
| `notifications/tools/list_changed` | Server 推送：工具列表变化 |

**Resources：**

| 方法 | 说明 |
| --- | --- |
| `resources/list` | 获取资源列表 |
| `resources/read` | 读取资源内容 |
| `resources/subscribe` | 订阅资源变更通知 |
| `resources/unsubscribe` | 取消订阅 |
| `notifications/resources/updated` | Server 推送：资源内容已更新 |
| `notifications/resources/list_changed` | Server 推送：资源列表变化 |

**Prompts：**

| 方法 | 说明 |
| --- | --- |
| `prompts/list` | 获取 Prompt 模板列表 |
| `prompts/get` | 获取指定 Prompt 内容 |
| `notifications/prompts/list_changed` | Server 推送：Prompt 列表变化 |

---

## 4. 快速开始

### 安装依赖

```bash
npm install @modelcontextprotocol/sdk zod
```

### 最简 MCP Server（Stdio 传输）

```typescript
import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { z } from 'zod';

const server = new McpServer({
  name: 'my-first-mcp',
  version: '1.0.0',
});

server.registerTool(
  'hello',
  { description: '打招呼', inputSchema: { name: z.string() } },
  async ({ name }) => ({
    content: [{ type: 'text', text: `Hello, ${name}!` }],
  }),
);

const transport = new StdioServerTransport();
await server.connect(transport);
```

---

## 5-11. 详细开发指南

包含：开发第一个 MCP Server、注册 Tools（工具）、注册 Resources（资源）、注册 Prompts（提示模板）、在 NestJS 中集成 MCP、调试与测试、最佳实践等完整内容。

### 项目相关地址

- 代码仓库：https://git.garena.com/shopee/seamoney-data/real-time/boussole/ai-tools
- SDP：https://space.shopee.io/console/cmdb/deployment/detail/shopee.fin_products.data.seamoneydata.ai-tools
- live域名：https://aitools.fp-data.shopee.io/mcp/:serviceId
- test域名：https://aitools.fp-data.test.shopee.io/mcp/:serviceId

### 项目目录结构

```
src/mcp/
├── interfaces/
│   └── mcp-server.interface.ts
├── servers/
│   ├── calculator/
│   ├── echo/
│   └── dashboard-screenshot/
├── mcp.controller.ts
├── mcp-registry.service.ts
├── mcp-session.service.ts
└── mcp.module.ts
```
