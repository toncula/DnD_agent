import os
import json
import time
from pathlib import Path
from dotenv import load_dotenv
from tqdm import tqdm

# LangChain 依赖
# [Change] 切换为 Google Gemini 的 Embeddings
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document

# 加载环境变量 (确保 .env 里有 GOOGLE_API_KEY)
load_dotenv()

# --- 配置路径 ---
BASE_DIR = Path(__file__).resolve().parents[2]
PROCESSED_DATA_PATH = BASE_DIR / "data" / "processed" / "dnd_knowledge_base.jsonl"
CHROMA_DB_DIR = BASE_DIR / "chroma_db_data"  # 向量库本地存储路径

# --- 配置参数 ---
BATCH_SIZE = 20  # 每次批量写入 100 条，防止内存溢出
COLLECTION_NAME = "dnd_rules"


def load_processed_data(file_path):
    """从 JSONL 读取数据并转换为 LangChain Document 对象"""
    documents = []
    if not file_path.exists():
        print(f"错误：找不到文件 {file_path}")
        return []

    print(f"正在读取数据: {file_path}...")
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            data = json.loads(line)

            # 创建 Document 对象
            # page_content 是用于检索的文本
            # metadata 是用于过滤的标签 (书名, 章节等)
            doc = Document(page_content=data["page_content"], metadata=data["metadata"])
            documents.append(doc)

    print(f"成功加载 {len(documents)} 条文档片段。")
    return documents


def ingest_data():
    """主入库流程"""

    # 1. 准备数据
    docs = load_processed_data(PROCESSED_DATA_PATH)
    if not docs:
        print("未找到数据，请先运行数据清洗脚本。")
        return

    # 2. 初始化 Embedding 模型
    # [Change] 使用 Google Gemini 的 embedding 模型
    # models/gemini-embedding-001 是目前 Google 最新的嵌入模型，支持多语言
    print("正在初始化 Gemini Embedding 模型 (models/gemini-embedding-001)...")
    try:
        embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
    except Exception as e:
        print(f"初始化模型失败: {e}")
        print("请检查 GOOGLE_API_KEY 是否正确配置，并确保已开通 Gemini API 权限。")
        return

    # 3. 初始化/连接 Chroma 向量库
    # persist_directory 指定数据存在本地哪里
    print(f"正在连接 ChromaDB (存储路径: {CHROMA_DB_DIR})...")
    vector_store = Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=str(CHROMA_DB_DIR),
    )

    # 4. 批量写入
    print(f"开始向量化并写入数据库 (Collection: {COLLECTION_NAME})...")
    total_docs = len(docs)

    # 我们可以把 batch size 稍微调大一点，Gemini 的速率限制通常比较宽容
    batch_size = 50

    for i in tqdm(range(0, total_docs, batch_size)):
        batch = docs[i : i + batch_size]

        try:
            # add_documents 会自动调用 Embedding API 并存储
            vector_store.add_documents(batch)
            # Gemini 的 QPM (每分钟查询数) 限制，稍微 sleep 一下比较稳妥
            time.sleep(1)
        except Exception as e:
            print(f"写入批次 {i} 时出错: {e}")
            # 简单的重试逻辑或跳过
            continue

    print(f"\n✅ 入库完成！共 {total_docs} 条数据已存入 ChromaDB。")


if __name__ == "__main__":
    # 检查 Key 是否存在
    if not os.getenv("GOOGLE_API_KEY"):
        print("错误：未找到 GOOGLE_API_KEY，请检查 .env 文件。")
        print("提示：你需要去 Google AI Studio 申请一个 API Key。")
    else:
        ingest_data()
