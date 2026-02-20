import sys
import os
import uuid
from pathlib import Path

# --- 确保 Python 能找到 src 模块 ---
BASE_DIR = Path(__file__).resolve().parents[2]
sys.path.append(str(BASE_DIR))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import chromadb

# 导入现有的 LangGraph Agent 和消息类型
from src.agent.graph import graph
from langchain_core.messages import HumanMessage, AIMessage

# --- 1. 初始化 FastAPI 应用 ---
app = FastAPI(
    title="D&D 5E 规则智能体 API",
    description="为前端提供 D&D 规则问答和目录检索的后端服务",
    version="1.0",
)

# 配置跨域请求 (CORS)，允许 Vue 等前端框架调用
origins = [
    "http://localhost:5173",  # Vite/Vue 默认开发端口
    "http://127.0.0.1:5173",
    "http://localhost:3000",  # React/Next.js 常用端口
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 2. 定义 Pydantic 数据模型 (API 契约) ---


class ChatMessage(BaseModel):
    role: str  # "user" 或 "assistant"
    content: str


class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    selected_books: List[str] = []
    thread_id: str = "default_thread"


class ToolLog(BaseModel):
    type: str  # 例如: "search_query" 或 "search_result"
    content: str


class ChatResponse(BaseModel):
    response: str
    logs: List[ToolLog]


# --- 3. 编写 API 接口 ---


@app.get("/health", summary="健康检查")
async def health_check():
    return {"status": "ok", "message": "D&D API Server is running!"}


@app.get("/v1/books", summary="获取规则书目录树")
async def get_book_tree():
    """
    扫描 ChromaDB 中的元数据，返回前端树形组件所需的规则书目录。
    该逻辑提取自原先的 app.py。
    """
    db_dir = BASE_DIR / "chroma_db_data"
    if not db_dir.exists():
        raise HTTPException(status_code=404, detail="未检测到本地向量数据库")

    try:
        client = chromadb.PersistentClient(path=str(db_dir))
        collection = client.get_collection("dnd_rules")

        # 获取所有的 metadata 以提取书名
        result = collection.get(include=["metadatas"])
        valid_books = set()
        for meta in result.get("metadatas", []):
            if meta and "source_book" in meta:
                valid_books.add(meta["source_book"])

        # 将扁平的书名路径转换为嵌套树结构
        tree = {}
        for path in valid_books:
            parts = path.split("/")
            current_level = tree
            for part in parts:
                if part not in current_level:
                    current_level[part] = {}
                current_level = current_level[part]

        def build_nodes(tree_dict, parent_path=""):
            nodes = []
            for name in sorted(tree_dict.keys()):
                subtree = tree_dict[name]
                current_path = f"{parent_path}/{name}" if parent_path else name

                node = {
                    "label": name,
                    "value": current_path,
                }
                if subtree:
                    node["children"] = build_nodes(subtree, current_path)
                nodes.append(node)
            return nodes

        nodes = build_nodes(tree)
        return {"nodes": nodes, "valid_paths": list(valid_books)}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"读取数据库失败: {str(e)}")


@app.post("/v1/chat", response_model=ChatResponse, summary="发起对话")
async def chat_endpoint(req: ChatRequest):
    """
    接收前端对话，调用 LangGraph Agent 处理，返回 AI 回答和工具调用日志。
    """
    if not req.messages:
        raise HTTPException(status_code=400, detail="消息列表不能为空")

    # 1. 将前端的 JSON 消息转换为 LangChain 的消息对象
    lc_messages = []
    for msg in req.messages:
        if msg.role == "user":
            lc_messages.append(HumanMessage(content=msg.content))
        elif msg.role == "assistant":
            lc_messages.append(AIMessage(content=msg.content))
        else:
            # 忽略系统消息或其他不支持的角色
            pass

    # 2. 准备 LangGraph 输入
    inputs = {"messages": lc_messages, "selected_books": req.selected_books}
    config = {"configurable": {"thread_id": req.thread_id}}

    full_response = ""
    logs = []

    try:
        # 3. 运行 Graph 并收集流式中间结果
        # recursion_limit 防止模型陷入无限查书的死循环
        for event in graph.stream(inputs, config={**config, "recursion_limit": 30}):
            for key, value in event.items():
                if key == "agent":
                    msg = value["messages"][-1]
                    # 判断是调用了工具，还是直接生成了文本
                    if hasattr(msg, "tool_calls") and msg.tool_calls:
                        tool_args = msg.tool_calls[0].get("args", {})
                        query = tool_args.get("query", "未知搜索词")
                        logs.append(
                            ToolLog(type="search_query", content=f"检索关键词: {query}")
                        )
                    else:
                        # 最终的回答
                        content = msg.content
                        if isinstance(content, list):
                            full_response = "".join(
                                [
                                    item.get("text", "")
                                    for item in content
                                    if isinstance(item, dict)
                                    and item.get("type") == "text"
                                ]
                            )
                        else:
                            full_response = str(content)

                elif key == "tools":
                    # 记录工具返回的结果摘要
                    msg = value["messages"][-1]
                    tool_content = msg.content
                    tool_text = str(tool_content)
                    if isinstance(tool_content, list):
                        tool_text = "".join(
                            [
                                item.get("text", "")
                                for item in tool_content
                                if isinstance(item, dict) and item.get("type") == "text"
                            ]
                        )

                    # 截断太长的结果，前端只作摘要展示
                    preview = (
                        tool_text[:150] + "..." if len(tool_text) > 150 else tool_text
                    )
                    logs.append(
                        ToolLog(type="search_result", content=f"查阅结果: {preview}")
                    )

        return ChatResponse(response=full_response, logs=logs)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent 运行出错: {str(e)}")


# 本地调试运行指令:
# uvicorn src.api.server:app --reload
