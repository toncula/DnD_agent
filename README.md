# D&D 5E 智能角色引擎 (DnD Agent)

这是一个结合了 **Google Gemini 3** 推理能力与 **Vite + Vue 3** 现代前端技术的龙与地下城 (D&D 5E) 数字化角色卡系统。它不仅提供了一个高度交互的角色面板，还集成了能够查阅多种规则书的 AI DM 顾问。

## 🚀 2026年2月重大更新

我们对系统进行了深度重构，带来了以下全新特性：

### 1. 现代化交互式角色面板
- **组件化重构**：将冗长的人物卡拆分为 `BioHeader` (身份)、`StatGrid` (属性)、`CombatStats` (战斗)、`SkillsSaves` (技能) 等多个独立模块。
- **静默自动同步**：引入了类似 Excel 的**防抖自动保存**机制。修改数值 1.2 秒后自动同步至后端，并静默回填派生数值（如 AC、调整值等），无需手动保存。
- **高密度 UI 布局**：针对跑团习惯优化了视觉层级，缩小了冗余间距，放大了核心战斗数值（HP、AC、先攻）。
- **智能生命值管理**：采用 `当前 / 上限 + 临时` 的直观显示格式，内置**死亡豁免**记录模块。
- **等级联动生命骰**：固定 20 级生命骰槽位，根据当前角色等级动态锁定/解锁编辑权限，并支持折叠隐藏。

### 2. 增强型 AI 规则顾问
- **模型升级**：全面接入最新的 **Gemini 3 Flash Preview** 模型，具备更强的逻辑推理和 Agent 协作能力。
- **智能规则书加载**：启动时自动勾选核心规则、战役设定和规则扩展，并在未选择任何规则书时禁止发送请求，避免无效查询。
- **动态规则库**：侧边栏支持基于 `source_book` 路径（如 `核心/玩家手册`）自动构建无限层级的目录树，支持级联勾选。
- **上下文感知**：AI 在回答时会优先参考您当前的人物卡状态，并根据您勾选的规则书范围进行精确检索。

---

## 🛠️ 快速开始

### 环境准备
1.  **Python 3.9+**
2.  **Node.js 18+**
3.  **Google API Key**: 在 `.env` 文件中配置您的 `GOOGLE_API_KEY`。

### 1. 启动后端 (Python FastAPI)
后端负责逻辑计算、向量数据库检索以及 JSON 数据的持久化。

```powershell
# 安装 Python 依赖
pip install -r requirements.txt

# 启动服务 (默认监听 8000 端口)
python src/api/server.py
```
*或者使用 uvicorn 开发模式：*
`uvicorn src.api.server:app --reload`

### 2. 启动前端 (Vite + Vue 3)
前端提供极致流畅的交互体验和实时同步反馈。

```powershell
# 进入根目录安装 Node 依赖
npm install

# 启动开发服务器 (默认监听 3000 端口)
npm run dev
```

### 3. 访问系统
在浏览器中打开：`http://localhost:3000/`

---

## 💡 使用技巧
- **同步指示灯**：右上角会显示“同步中...”状态。当显示“已同步”并自动淡出时，表示您的数据已安全存入后端。
- **隐藏侧边栏**：点击左上角的“面板”图标或侧边悬浮箭头，可以收起规则书库，获得更大的操作视野。
- **召唤助手**：点击右上角“召唤助手”展开 AI 对话框，您可以问它：“以我现在的属性，跳远能跳多远？”

## 🗂️ 技术栈
- **Frontend**: Vue 3, TypeScript, Vite, Tailwind CSS v4, Lucide Icons
- **Backend**: FastAPI, Pydantic v2, LangChain, LangGraph
- **AI/LLM**: Google Gemini 3 Flash Preview, Gemini Embeddings
- **Database**: ChromaDB (Vector Store)
