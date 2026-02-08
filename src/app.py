import sys
import os
import uuid
from pathlib import Path
import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage
import chromadb

# --- [新增] 0. 网络代理配置 ---
# os.environ["HTTP_PROXY"] = "http://127.0.0.1:7890"
# os.environ["HTTPS_PROXY"] = "http://127.0.0.1:7890"

# --- 新增依赖 ---
try:
    from streamlit_tree_select import tree_select
except ImportError:
    st.error("请安装依赖库: `pip install streamlit-tree-select` 以使用树形选择器")
    st.stop()

# --- 1. 环境与路径配置 ---
BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(BASE_DIR))

from src.agent.graph import graph


@st.cache_data
def get_book_tree_nodes():
    """
    [核心修改]
    不再扫描 data/raw (部署环境可能没有)，而是直接从 chroma_db_data 读取元数据。
    这样能保证前端显示的目录与数据库实际内容完全一致。
    """
    db_dir = BASE_DIR / "chroma_db_data"

    if not db_dir.exists():
        # 如果连数据库都没有，说明完全没初始化
        return [], set()

    valid_books = set()

    try:
        # 1. 连接本地 ChromaDB
        client = chromadb.PersistentClient(path=str(db_dir))
        # 获取集合 (名称必须与 ingest.py 中一致，默认为 'dnd_rules')
        collection = client.get_collection("dnd_rules")

        # 2. 获取所有数据的元数据 (只拿 metadata，速度很快)
        # include=["metadatas"] 避免加载庞大的向量数据
        result = collection.get(include=["metadatas"])

        # 3. 提取唯一的 source_book 字段
        for meta in result["metadatas"]:
            if "source_book" in meta:
                valid_books.add(meta["source_book"])

    except Exception as e:
        st.error(f"读取数据库目录失败: {e}")
        return [], set()

    # 4. 将扁平的 source_book 列表转换为嵌套字典树
    # (后续逻辑保持不变，因为 source_book 的格式就是 'Category/Book')
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
    return nodes, valid_books


# --- 3. Streamlit 页面设置 ---
st.set_page_config(page_title="D&D 5E 规则智能体", page_icon="🐉", layout="wide")

st.title("🐉 D&D 5E 规则智能助手 (Agentic RAG)")

# --- 4. 侧边栏 ---
with st.sidebar:
    st.header("📚 规则书库配置")

    nodes, valid_book_paths = get_book_tree_nodes()

    if not nodes:
        st.warning("未检测到 data/raw 数据，请先运行 ETL 脚本。")
        final_selected_books = []
    else:
        st.caption("👇 点击箭头展开文件夹，勾选框可全选/反选")
        return_val = tree_select(
            nodes,
            checked=[path for path in valid_book_paths],
            expanded=[],
            check_model="all",
            no_cascade=False,
        )
        selected_ids = return_val["checked"]
        final_selected_books = [bid for bid in selected_ids if bid in valid_book_paths]

        if st.checkbox("显示已选书目详情", value=False):
            st.write(final_selected_books)
            st.write(f"共选中 {len(final_selected_books)} 本书")

# --- 5. 聊天界面逻辑 ---

if "messages" not in st.session_state:
    st.session_state.messages = []
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

for msg in st.session_state.messages:
    if isinstance(msg, HumanMessage):
        st.chat_message("user").write(msg.content)
    elif isinstance(msg, AIMessage):
        st.chat_message("assistant").write(msg.content)

if prompt := st.chat_input("请问 Dungeon Master... (例如: 法师几级学火球术?)"):
    st.chat_message("user").write(prompt)
    st.session_state.messages.append(HumanMessage(content=prompt))

    inputs = {
        "messages": st.session_state.messages,
        "selected_books": final_selected_books,
    }

    config = {"configurable": {"thread_id": st.session_state.thread_id}}

    with st.chat_message("assistant"):
        status_container = st.status("🎲 DM 正在翻阅规则书...", expanded=True)
        response_placeholder = st.empty()
        full_response = ""

        try:
            # [修改] recursion_limit 设置为 30，给后端 5 次重试留足空间
            for event in graph.stream(inputs, config={**config, "recursion_limit": 30}):
                for key, value in event.items():
                    if key == "agent":
                        msg = value["messages"][-1]
                        if msg.tool_calls:
                            tool_args = msg.tool_calls[0]["args"]
                            status_container.write(
                                f"🔍 **检索请求**: `{tool_args.get('query', '')}`"
                            )

                            books_filter = tool_args.get("book_filter", [])
                            if books_filter and len(books_filter) > 3:
                                book_display = (
                                    f"{books_filter[0]} 等 {len(books_filter)} 本书"
                                )
                            else:
                                book_display = str(books_filter)
                            status_container.write(f"📚 **范围**: `{book_display}`")
                        else:
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
                        msg = value["messages"][-1]
                        tool_content = msg.content
                        if isinstance(tool_content, list):
                            tool_text = "".join(
                                [
                                    item.get("text", "")
                                    for item in tool_content
                                    if isinstance(item, dict)
                                    and item.get("type") == "text"
                                ]
                            )
                        else:
                            tool_text = str(tool_content)
                        preview = (
                            tool_text[:200] + "..."
                            if len(tool_text) > 200
                            else tool_text
                        )
                        status_container.markdown(f"📄 **查阅结果**: \n> {preview}")

            status_container.update(
                label="✅ 回答生成完毕", state="complete", expanded=False
            )
            response_placeholder.markdown(full_response)
            st.session_state.messages.append(AIMessage(content=full_response))

        except Exception as e:
            status_container.update(label="❌ 发生错误", state="error")
            st.error(f"Agent 运行出错: {str(e)}")
