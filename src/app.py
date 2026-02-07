import sys
import os
import uuid
from pathlib import Path
import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage

# --- [新增] 0. 网络代理配置 (解决连接被切断的问题) ---
# 如果您在中国大陆使用 Google API，必须配置代理。
# 请根据您的 VPN 软件查看端口号 (常见的有 7890, 10809, 4780 等)
# 如果您不需要代理，请注释掉这两行。
# os.environ["HTTP_PROXY"] = "http://127.0.0.1:7890"
# os.environ["HTTPS_PROXY"] = "http://127.0.0.1:7890"

# --- 新增依赖 ---
# 如果运行报错，请执行: pip install streamlit-tree-select
try:
    from streamlit_tree_select import tree_select
except ImportError:
    st.error("请安装依赖库: `pip install streamlit-tree-select` 以使用树形选择器")
    st.stop()

# --- 1. 环境与路径配置 ---
BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(BASE_DIR))

from src.agent.graph import graph


# --- 2. 辅助函数：构建树形结构 ---
@st.cache_data
def get_book_tree_nodes():
    """
    扫描 data/raw 目录，构建用于 tree_select 的节点结构
    同时返回所有有效的叶子节点集合（用于后续过滤）
    """
    raw_dir = BASE_DIR / "data" / "raw"
    if not raw_dir.exists():
        return [], set()

    # 1. 获取所有有效的 source_book 路径
    # 例如: ["核心规则/玩家手册2024", "扩展/XGE", "核心规则/DMG"]
    # 只要文件夹下有 htm 文件，它就是一个 valid_book
    valid_books = set()
    for file_path in raw_dir.rglob("**/*.htm*"):
        if file_path.is_dir():
            continue
        try:
            relative_path = file_path.parent.relative_to(raw_dir)
            book_path = relative_path.as_posix()
            if book_path != ".":
                valid_books.add(book_path)
        except Exception:
            continue

    # 2. 将扁平路径转换为嵌套字典树
    tree = {}
    for path in valid_books:
        parts = path.split("/")
        current_level = tree
        for part in parts:
            if part not in current_level:
                current_level[part] = {}
            current_level = current_level[part]

    # 3. 递归转换为 streamlit-tree-select 需要的格式
    def build_nodes(tree_dict, parent_path=""):
        nodes = []
        for name, subtree in tree_dict.items():
            # 构建当前节点的完整路径 ID
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

# [修改] 使用滤镜反转方案 (Filter Invert) 将黑字强制变为白字
# 使用了更广泛的选择器确保生效
st.markdown(
    """
    <style>
    /* 1. 侧边栏全局文字颜色 */
    [data-testid="stSidebar"] {
        color: white !important;
    }
    
    /* 2. 针对侧边栏内所有 iframe 组件 (包括 tree-select) 进行颜色反转 */
    /* 原理：组件默认是透明背景+黑色字 */
    /* invert(1): 黑色字 -> 白色字 */
    /* hue-rotate(180deg): 把被反转的红色勾选框(变青色了)再转回红色 */
    [data-testid="stSidebar"] iframe {
        filter: invert(1) hue-rotate(180deg);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("🐉 D&D 5E 规则智能助手 (Agentic RAG)")

# --- 4. 侧边栏：VS Code 风格的树形选择器 ---
with st.sidebar:
    st.header("📚 规则书库配置")

    nodes, valid_book_paths = get_book_tree_nodes()

    if not nodes:
        st.warning("未检测到 data/raw 数据，请先运行 ETL 脚本。")
        final_selected_books = []
    else:
        st.caption("👇 点击箭头展开文件夹，勾选框可全选/反选")

        # 渲染树形组件
        # 注意：tree_select 必须在 with st.sidebar 块内部调用才能显示在侧边栏
        return_val = tree_select(
            nodes,
            checked=[path for path in valid_book_paths],  # 默认全选所有书
            expanded=[],  # 默认折叠
            # [核心修改] 将 check_model 改为 "all"
            # "leaf": 只返回选中的子节点 (会导致父文件夹被忽略)
            # "all": 返回所有被选中的节点 (包含父文件夹 ID)
            check_model="all",
            no_cascade=False,  # 开启级联选择（父选子选）
        )

        # 获取用户勾选的所有 ID (包含父文件夹 ID 和叶子节点 ID)
        selected_ids = return_val["checked"]

        # 过滤：只保留真正对应“书”的 ID
        # 这里的 valid_book_paths 包含了所有含有 .htm 文件的目录路径
        # 如果父文件夹含有文件，它就在 valid_book_paths 里，会被保留
        # 如果父文件夹只是个空壳，它不在 valid_book_paths 里，会被剔除
        final_selected_books = [bid for bid in selected_ids if bid in valid_book_paths]

        # 调试信息
        if st.checkbox("显示已选书目详情", value=False):
            st.write(final_selected_books)
            st.write(f"共选中 {len(final_selected_books)} 本书")

# --- 5. 聊天界面逻辑 ---

# 初始化 Session State
if "messages" not in st.session_state:
    st.session_state.messages = []
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

# 渲染历史消息
for msg in st.session_state.messages:
    if isinstance(msg, HumanMessage):
        st.chat_message("user").write(msg.content)
    elif isinstance(msg, AIMessage):
        st.chat_message("assistant").write(msg.content)

# 处理用户输入
if prompt := st.chat_input("请问 Dungeon Master... (例如: 法师几级学火球术?)"):
    st.chat_message("user").write(prompt)
    st.session_state.messages.append(HumanMessage(content=prompt))

    # 准备 Agent 输入
    inputs = {
        "messages": st.session_state.messages,
        "selected_books": final_selected_books,
    }

    config = {"configurable": {"thread_id": st.session_state.thread_id}}

    # 运行 Agent
    with st.chat_message("assistant"):
        status_container = st.status("🎲 DM 正在翻阅规则书...", expanded=True)
        response_placeholder = st.empty()
        full_response = ""

        try:
            for event in graph.stream(inputs, config=config):
                for key, value in event.items():
                    if key == "agent":
                        msg = value["messages"][-1]
                        if msg.tool_calls:
                            tool_args = msg.tool_calls[0]["args"]
                            status_container.write(
                                f"🔍 **检索请求**: `{tool_args.get('query', '')}`"
                            )

                            # 优化显示：如果书太多，只显示数量
                            books_filter = tool_args.get("book_filter", [])
                            if books_filter and len(books_filter) > 3:
                                book_display = (
                                    f"{books_filter[0]} 等 {len(books_filter)} 本书"
                                )
                            else:
                                book_display = str(books_filter)
                            status_container.write(f"📚 **范围**: `{book_display}`")
                        else:
                            # 修复 Gemini 内容为列表的问题
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
