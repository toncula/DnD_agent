import os
from pathlib import Path
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.tools import tool

load_dotenv()

# --- 配置路径 (指向之前生成的 chroma_db_data) ---
BASE_DIR = Path(__file__).resolve().parents[2]
CHROMA_DB_DIR = BASE_DIR / "chroma_db_data"
COLLECTION_NAME = "dnd_rules"

# --- 初始化向量库连接 ---
# [重要] 必须使用和入库时 (src/db/ingest.py) 完全相同的模型名称
embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")

if not CHROMA_DB_DIR.exists():
    raise FileNotFoundError(f"未找到向量库数据: {CHROMA_DB_DIR}，请先运行入库脚本。")

vector_store = Chroma(
    collection_name=COLLECTION_NAME,
    embedding_function=embeddings,
    persist_directory=str(CHROMA_DB_DIR),
)


@tool
def search_rules(query: str, book_filter: list[str] = None):
    """
    检索 D&D 5E 规则书的专用工具。

    Args:
        query: 具体的搜索关键词 (例如: "火球术 伤害", "野蛮人 狂暴 机制").
        book_filter: 限制搜索的规则书列表 (例如: ["PHB", "XGE"]). 如果为 None，则搜索所有书.
    """
    print(
        f"\n[Tool] 正在检索: {query} | 范围: {book_filter if book_filter else '全部'}"
    )

    filter_dict = {}
    # 构建 ChromaDB 的 Metadata 过滤器
    if book_filter:
        if len(book_filter) == 1:
            filter_dict = {"source_book": book_filter[0]}
        else:
            filter_dict = {"source_book": {"$in": book_filter}}

    # 执行相似度搜索
    # k=5 表示返回 5 个最相关的片段
    try:
        results = vector_store.similarity_search(
            query, k=5, filter=filter_dict if filter_dict else None
        )
    except Exception as e:
        return f"检索出错: {str(e)}"

    if not results:
        return "未在指定的规则书中找到相关内容。"

    # 格式化返回结果给 LLM 看
    formatted_results = []
    for doc in results:
        source = f"{doc.metadata.get('source_book', 'Unknown')} > {doc.metadata.get('chapter', 'Unknown')}"
        # 在内容前加上来源标注，方便 LLM 引用
        content = f"--- 来源: {source} ---\n{doc.page_content}\n"
        formatted_results.append(content)

    return "\n".join(formatted_results)
