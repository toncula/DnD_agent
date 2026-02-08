# 🐉 D&D 5E 规则智能助手 (Agentic RAG)

这是一个基于 Agentic RAG (代理式检索增强生成) 技术构建的龙与地下城 (D&D 5E) 规则问答智能体。

不同于传统的关键词搜索或简单的 RAG，本智能体采用 LangGraph 构建了具备思考能力的 Agent。它能够理解复杂的规则问题，主动规划检索步骤，在多本规则书中查找信息，并进行逻辑推理（如计算法术伤害、比较职业特性），最终给出精准的中文规则解答。

## ✨ 核心特性

🧠 Agentic Workflow: 基于 LangGraph 的循环图结构，支持“思考-行动-观察”循环。如果第一次检索结果不满意，Agent 会自动尝试新的关键词。

📚 多书目精准筛选: 前端提供类似 VS Code 的树形文件选择器，支持按文件夹（如“核心规则”）或单本书（如“玩家手册2024”）进行检索范围限制。

📖 结构化数据清洗: 专门针对 D&D HTML/CHM 源文件设计的 ETL 流水线，将 HTML 转换为 Markdown，完美保留表格和标题层级，大幅提升 LLM 理解能力。

🔍 智能防死循环: 内置软性熔断机制和历史搜索记忆，防止 Agent 在检索不到内容时陷入无限循环。

💎 Google Gemini 驱动: 全程使用 Gemini 3 flash preview (逻辑推理) 和 gemini Embedding 001 (向量化)，成本极低且上下文窗口巨大。

## 🛠️ 技术栈

LLM: Google Gemini 3 flash preview

Embedding: Google gemini Embedding 001

Orchestration: LangChain, LangGraph

Vector DB: ChromaDB

Frontend: Streamlit + streamlit-tree-select

ETL: BeautifulSoup4, Markdownify

## 🚀 快速开始

推荐使用 Python 3.10 或 3.11。

### 创建并激活 Conda 环境

```bash
conda create -n dnd-agent python=3.11
conda activate dnd-agent
```

### 安装依赖

```bash
pip install -r requirements.txt
```

### 配置环境变量

在项目根目录创建 .env 文件，并填入您的 Google API Key：

GOOGLE_API_KEY="AIzaSy..."

LANGSMITH_API_KEY="..."  (可选) 用于调试监控

### 数据准备 (ETL)

本项目包含2026/2月版本的DND5e_chm的JSONL数据。如果您想使用最新的规则书版本或自定义内容，请按照以下步骤进行数据清洗和入库。

您需要自行准备 D&D 5E 的 HTML 源文件（推荐使用 DND5e_chm 项目的源文件）。

#### 步骤 A: 放置原始文件

将 HTML 文件夹放入 data/raw/ 目录中。结构如下：

```
data/
└── raw/
    ├── 核心规则/
    │   ├── 玩家手册2024/
    │   └── 地下城主指南/
    └── 规则扩展/
        └── 萨娜萨的万事指南/
```

#### 步骤 B: 清洗数据

运行清洗脚本，将 HTML 转换为结构化的 JSONL：

```bash
python src/etl/processor.py
```

输出：data/processed/dnd_knowledge_base.jsonl

#### 步骤 C: 向量入库

将清洗后的数据写入 ChromaDB：

```bash
python src/db/ingest.py
```

输出：chroma_db_data/ 文件夹

### 启动应用

运行 Streamlit 前端：

```bash
streamlit run src/app.py
```

浏览器将自动打开 <http://localhost:8501。>

## 📂 项目结构

```
dnd-agent/
├── .env                    # 环境变量 (不要提交到 Git)
├── chroma_db_data/         # 向量数据库本地存储
├── data/
│   ├── raw/                # 原始 HTML 文件存放处
│   └── processed/          # 清洗后的 JSONL 文件
├── src/
│   ├── agent/
│   │   ├── graph.py        # Agent 核心逻辑 (LangGraph)
│   │   └── tools.py        # 检索工具定义
│   ├── db/
│   │   └── ingest.py       # 向量入库脚本
│   ├── etl/
│   │   └── processor.py    # 数据清洗脚本 (HTML -> Markdown)
│   └── app.py              # Streamlit 前端应用
└── requirements.txt        # 依赖列表
```

## ⚠️ 常见问题

Q: 遇到 Server disconnected 或 ConnectTimeout 错误？
A: 这是因为 Python 脚本无法自动读取系统代理，导致连接 Google API 失败。
请在 src/app.py 和 src/agent/graph.py 的顶部设置代理代码：

Q: 搜索结果为空？
A: 请检查左侧侧边栏是否勾选了正确的规则书。如果勾选了仍为空，可能是数据库元数据不匹配。请尝试删除 chroma_db_data 文件夹后重新运行 ETL 和入库脚本。

Q: 表格显示乱码？
A: 我们使用 Markdown 表格存储。Gemini 生成回答时通常会正确渲染 Markdown，但在某些情况下如果源 HTML 表格极其复杂，可能会有格式损失。

## 🤝 贡献

欢迎提交 Issue 或 Pull Request 来改进 Agent 的 Prompt 或数据清洗逻辑！

## 📄 License

GPL-3.0 License
