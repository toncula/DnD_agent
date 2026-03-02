# D&D 5E 智能角色引擎 (DnD Agent)

这是一个结合了 **Google Gemini 3** 推理能力与 **Vite + Vue 3** 现代前端技术的龙与地下城 (D&D 5E) 数字化角色卡系统。它不仅提供了一个高度交互的角色面板，还集成了能够查阅多种规则书的 AI DM 顾问。

## 🚀 2026年3月重大更新 (核心引擎升级)

我们对战斗引擎和角色模型进行了深度重构，带来了符合 5E 专业标准的自动化体验：

### 1. 深度自动化战斗引擎
- **多职业兼职系统 (Multiclassing)**：内置标准 5E **有效施法者等级 (ECL)** 计算逻辑。支持全职、半职、三分之一职以及游侠/人工技师的特殊取整规则，自动生成 1-20 级的法术位表。
- **纸娃娃装备同步 (Paper-Doll Sync)**：实现背包与战斗面板的**双向实时同步**。
    - **双手武器逻辑**：装备双手武器会自动占据副手槽位并卸下盾牌。
    - **AC 自动重算**：根据当前穿着的轻/中/重甲及盾牌状态，结合敏捷修正值（及中甲上限）实时重算防御等级。
- **职业特殊资源追踪**：新增气点 (Ki)、激励 (Inspiration)、荒野变形 (Wild Shape) 等动态资源气泡追踪器，支持短休/长休重置逻辑。

### 2. 标准化法术管理系统 (Spellcasting 2.0)
- **5E 标准化字段**：法术模型现已补全：**法术系别、施法时间、距离、成分(V/S/M)、材料详情、持续时间**及详细说明。
- **高级准备逻辑**：
    - **恒定准备 (Always Prepared)**：支持领域法术等“恒定准备”特性，不占用每日准备法术限额。
    - **独立属性覆盖**：支持为单个法术指定独立的施法属性（智力/感知/魅力），完美适配“专长获得”或“奇物赋予”的法术。
- **全局施法设置**：在战斗页面可一键切换全局施法属性，实时重算法术 DC 和攻击加值。

### 3. 现代化交互式角色面板
- **组件化重构**：将冗长的人物卡拆分为 `BioHeader`、`StatGrid`、`CombatStats`、`SkillsSaves` 等多个高内聚模块。
- **静默自动同步**：引入类似 Excel 的防抖同步机制，修改数值 1.2 秒后自动存入后端并更新全表派生数值。
- **高密度 UI 布局**：针对跑团实操优化，显著提升了核心战斗数值（HP、AC、先攻）的视觉层级。

---

## 🛠️ 快速开始

### 环境准备
1.  **Python 3.9+**
2.  **Node.js 18+**
3.  **Google API Key**: 在 `.env` 文件中配置您的 `GOOGLE_API_KEY`。

### 1. 启动后端 (Python FastAPI)
```powershell
pip install -r requirements.txt
python src/api/server.py
```

### 2. 启动前端 (Vite + Vue 3)
```powershell
npm install
npm run dev
```

### 3. 访问系统
在浏览器中打开：`http://localhost:3000/`

---

## 💡 使用技巧
- **同步指示灯**：右上角显示“同步中...”状态。当显示“已同步”时，表示数据已安全存入后端。
- **隐藏侧边栏**：点击左上角的“面板”图标可收起规则书库，获得更大视野。
- **召唤助手**：点击右上角“召唤助手”展开 AI 对话框。AI 已具备感知您当前人物卡状态的能力。

## 🗂️ 技术栈
- **Frontend**: Vue 3, TypeScript, Vite, Tailwind CSS v4, Lucide Icons
- **Backend**: FastAPI, Pydantic v2, LangChain, LangGraph
- **AI/LLM**: Google Gemini 3 Flash Preview, Gemini Embeddings
- **Database**: ChromaDB (Vector Store)
