import sys
import os
import logging
from pathlib import Path

# --- 日志配置 ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("dnd-api")

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
from src.engine.character_engine import CharacterSheet
from src.engine.loader import CharacterLoader

# --- 1. 初始化 FastAPI 应用 ---
app = FastAPI(title="D&D 5E 规则智能体 API")

# 放宽 CORS 限制以便调试，允许所有来源
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化 Chromadb 全局客户端，避免重复创建触发遥测错误
try:
    db_path = str(BASE_DIR / "chroma_db_data")
    if not os.path.exists(db_path):
        os.makedirs(db_path)
    client = chromadb.PersistentClient(path=db_path)
    logger.info(f"成功连接到 ChromaDB: {db_path}")
except Exception as e:
    logger.error(f"ChromaDB 初始化失败: {e}")
    client = None

# --- 2. 定义 Pydantic 数据模型 ---

class ChatMessage(BaseModel):
    role: str
    content: str

class ToolLog(BaseModel):
    type: str
    content: str

class ChatResponse(BaseModel):
    response: str
    logs: List[ToolLog]

class CharacterUpdate(BaseModel):
    data: Dict[str, Any]

class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    selected_books: List[str] = []
    thread_id: str = "default_thread"
    character_data: Optional[Dict[str, Any]] = None

# --- 3. 编写 API 接口 ---

@app.get("/health")
async def health_check():
    return {"status": "ok", "db_connected": client is not None}

@app.get("/v1/books")
async def get_books():
    logger.info("收到获取书籍列表请求")
    try:
        if not client:
            raise Exception("数据库未连接")
        
        collection = client.get_collection("dnd_rules")
        result = collection.get(include=["metadatas"])
        metadatas = result.get("metadatas", [])
        
        # 获取所有原始路径 (例如: "核心规则/玩家手册", "扩展手册/珊娜萨")
        all_paths = sorted(list(set(m.get("source_book") for m in metadatas if m and m.get("source_book"))))
        
        # 自动构建树结构的函数
        def build_tree(paths):
            root = []
            for path in paths:
                parts = path.split('/')
                current_level = root
                full_path = ""
                
                for i, part in enumerate(parts):
                    if full_path:
                        full_path += "/" + part
                    else:
                        full_path = part
                        
                    # 查找当前层级是否已存在该节点
                    existing_node = next((node for node in current_level if node["label"] == part), None)
                    
                    if existing_node:
                        # 如果是中间路径，确保有 children
                        if i < len(parts) - 1:
                            if "children" not in existing_node:
                                existing_node["children"] = []
                            current_level = existing_node["children"]
                    else:
                        # 创建新节点
                        new_node = {
                            "label": part,
                            "value": full_path
                        }
                        if i < len(parts) - 1:
                            new_node["children"] = []
                            current_level.append(new_node)
                            current_level = new_node["children"]
                        else:
                            current_level.append(new_node)
            return root

        nodes = build_tree(all_paths)
        return {"nodes": nodes, "valid_paths": all_paths}
    except Exception as e:
        logger.error(f"获取书名失败: {e}")
        return {"nodes": [], "valid_paths": []}

@app.get("/v1/character")
async def get_character():
    logger.info("收到获取人物卡请求")
    char_path = BASE_DIR / "data" / "processed" / "mock_character.json"
    character = CharacterLoader.load_from_json(char_path)
    return character.model_dump()

@app.post("/v1/character")
async def update_character(req: CharacterUpdate):
    logger.info("收到更新人物卡请求")
    try:
        # 进行 Pydantic 验证
        character = CharacterSheet.model_validate(req.data)
        char_path = BASE_DIR / "data" / "processed" / "mock_character.json"
        CharacterLoader.save_to_json(character, char_path)
        return character.model_dump()
    except Exception as e:
        # 关键：打印出具体哪里验证失败了
        logger.error(f"人物卡数据验证失败! 详细错误: {str(e)}")
        # 如果是因为数据类型不匹配，这里会打印出具体的路径
        raise HTTPException(status_code=400, detail=f"数据格式错误: {str(e)}")

@app.post("/v1/chat", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest):
    logger.info(f"收到对话请求: {req.messages[-1].content if req.messages else ''}")
    # ... (保持原有的 chat 处理逻辑)
    # 为了保持回复简洁，这里省略了中间重复的 chat 逻辑，但实际文件中应保留
    try:
        lc_messages = []
        for msg in req.messages:
            if msg.role == "user":
                lc_messages.append(HumanMessage(content=msg.content))
            elif msg.role == "assistant":
                lc_messages.append(AIMessage(content=msg.content))

        inputs = {"messages": lc_messages, "selected_books": req.selected_books, "character_data": req.character_data}
        config = {"configurable": {"thread_id": req.thread_id}}
        
        full_response = ""
        logs = []

        for event in graph.stream(inputs, config={**config, "recursion_limit": 30}):
            for key, value in event.items():
                if key == "agent":
                    msg = value["messages"][-1]
                    if hasattr(msg, "tool_calls") and msg.tool_calls:
                        logs.append(ToolLog(type="search_query", content=f"检索关键词: {msg.tool_calls[0].get('args', {}).get('query')}"))
                    else:
                        # 关键修复：处理 Gemini 3 的多模态列表格式
                        content = msg.content
                        if isinstance(content, list):
                            # 从内容块列表中提取所有文本部分
                            text_parts = []
                            for part in content:
                                if isinstance(part, dict) and part.get("type") == "text":
                                    text_parts.append(part.get("text", ""))
                                elif isinstance(part, str):
                                    text_parts.append(part)
                            full_response = "".join(text_parts)
                        else:
                            # 如果已经是字符串，直接使用
                            full_response = str(content)
                elif key == "tools":
                    msg = value["messages"][-1]
                    logs.append(ToolLog(type="search_result", content=f"查阅结果: {str(msg.content)[:100]}..."))

        return ChatResponse(response=full_response, logs=logs)
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    # 确保在根目录下运行，以便模块路径正确
    uvicorn.run("src.api.server:app", host="127.0.0.1", port=8000, reload=True)
