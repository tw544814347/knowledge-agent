# 知识库 Agent 前端

基于 React + Vite + Tailwind CSS 的暗色系聊天交互界面，对接后端 RAG 问答服务。

## 技术栈

| 技术 | 版本 | 用途 |
|------|------|------|
| React | 19.x | UI 框架 |
| Vite | 6.x | 构建工具 |
| Tailwind CSS | 4.x | 样式框架 |
| react-markdown | - | Markdown 渲染（支持表格、代码高亮） |
| react-syntax-highlighter | - | 代码块语法高亮 |
| lucide-react | - | 图标库 |

## 功能特性

- **暗色系 UI**：深色背景配色，护眼舒适
- **实时问答**：输入问题，调用后端 RAG API 获取回答
- **Markdown 渲染**：支持标题、表格、代码块、列表、引用等
- **来源引用**：每条回答展示检索命中的知识文档及相关度
- **打字动画**：AI 生成回答时的 loading 动画
- **快捷操作**：Enter 发送、Shift+Enter 换行、一键复制回答
- **侧边栏**：服务状态、知识库信息、增量同步/重建索引
- **推荐问题**：空白页面展示推荐问题，快速开始

## 快速启动

### 前置条件

1. Node.js >= 18
2. 后端 API 服务已启动（默认 `http://localhost:8000`）

### 安装和运行

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 启动开发服务器（端口 3000）
npm run dev
```

浏览器访问 `http://localhost:3000` 即可使用。

### 一键启动（前后端同时）

```bash
# 终端 1：启动后端
cd /path/to/知识库\ agent
python scripts/run_server.py

# 终端 2：启动前端
cd /path/to/知识库\ agent/frontend
npm run dev
```

## 架构说明

```
frontend/
├── src/
│   ├── main.jsx              # 入口
│   ├── App.jsx               # 根组件（状态管理、服务检测）
│   ├── api.js                # API 调用封装
│   ├── index.css             # 全局样式（Tailwind + 自定义 CSS 变量）
│   └── components/
│       ├── ChatPanel.jsx     # 聊天主面板（消息列表 + 输入框）
│       ├── MessageBubble.jsx # 消息气泡（Markdown 渲染 + 来源 + 复制）
│       └── Sidebar.jsx       # 侧边栏（状态 + 操作）
├── index.html
├── vite.config.js            # Vite 配置（代理 /api → 后端）
└── package.json
```

### 数据流

```
用户输入 → ChatPanel.handleSend()
         → api.askQuestion() → POST /api/v1/ask
         → 后端 RAG Pipeline → 返回 { answer, sources }
         → MessageBubble 渲染（Markdown + 来源标签）
```

### API 代理

开发模式下 Vite 自动代理 `/api` 和 `/health` 请求到后端 `http://localhost:8000`，无需处理跨域问题。

## 配置

### 修改后端地址

编辑 `vite.config.js` 中的 `proxy.target`：

```js
proxy: {
  '/api': {
    target: 'http://localhost:8000', // 修改为你的后端地址
    changeOrigin: true,
  },
}
```

### 主题色

编辑 `src/index.css` 中的 `@theme` 块，可自定义暗色系配色：

```css
@theme {
  --color-dark-900: #0d1117;    /* 最深背景 */
  --color-accent: #58a6ff;       /* 强调色 */
  --color-user-bubble: #1f6feb;  /* 用户消息气泡 */
  /* ... */
}
```

## 构建部署

```bash
npm run build
```

产物在 `dist/` 目录，可部署到 Nginx 或直接由 FastAPI 提供静态文件服务。
