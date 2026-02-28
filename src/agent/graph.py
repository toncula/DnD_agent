from typing import Annotated, Literal, TypedDict, Optional, Dict, Any

from dotenv import load_dotenv

import sys
import os
#os.environ["HTTP_PROXY"] = "http://127.0.0.1:7890"
#os.environ["HTTPS_PROXY"] = "http://127.0.0.1:7890"
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))


# 引入 Gemini 模型

from langchain_google_genai import ChatGoogleGenerativeAI


# 引入 LangGraph 组件

from langgraph.graph import StateGraph, START, END

from langgraph.graph.message import add_messages

from langgraph.prebuilt import ToolNode, tools_condition

from langchain_core.messages import HumanMessage, SystemMessage, AnyMessage, AIMessage

from langgraph.checkpoint.memory import MemorySaver


# 引入刚才定义的工具

from src.agent.tools import search_rules


load_dotenv()


# --- 1. 定义状态 (State) ---

# 这是 Agent 在思考过程中维护的数据结构


class AgentState(TypedDict):

    # [关键修改] 使用 add_messages 确保消息是追加而不是覆盖

    # 这样 Agent 在执行工具后还能记得用户最初的问题

    messages: Annotated[list[AnyMessage], add_messages]

    selected_books: list[str]  # 用户勾选的规则书 (从前端传入)

    character_data: Optional[Dict[str, Any]]  # 人物卡数据


# --- 2. 初始化模型与工具 ---

tools = [search_rules]


llm = ChatGoogleGenerativeAI(
    model="gemini-3-flash-preview", 
    temperature=0, 
    max_retries=3,
    timeout=60
)


# 将工具绑定给 LLM，让它知道自己能干什么

llm_with_tools = llm.bind_tools(tools)


# --- 3. 定义节点 (Nodes) ---


def reasoner(state: AgentState):
    """

    大脑节点：LLM 决定是回答问题还是调用工具

    """

    # 从状态中获取用户选择的规则书

    books = state.get("selected_books", [])
    character = state.get("character_data", {})

    messages = state["messages"]

    base_system_prompt = f"""你是一个精通 D&D 5E (龙与地下城) 中文规则的地下城主(DM)助手。

    **当前人物卡信息**:
    {character if character else "暂未加载人物卡"}

    **当前环境限制**:

    用户仅允许你参考以下规则书: {books if books else '所有可用规则书'}。

    **你的行动准则**:
    1. **参考人物卡**: 当用户问到关于“我”或当前角色时，请优先查看上面的**当前人物卡信息**。
    2. **必须查书**: 遇到规则问题，必须调用 `search_rules` 工具检索，严禁仅凭记忆或臆造回答。
    3. **参数传递**: 调用工具时，必须将上面的规则书列表准确传递给 `book_filter` 参数。
    4. **具体胜过一般**: 如果检索结果中，职业特性/专长描述与通用战斗规则冲突，以具体的特性为准 (Specific Beats General)。
    5. **引用来源**: 回答必须注明信息来源（例如：根据《玩家手册》第x章...）。
    6. **诚实**: 如果查不到，就说查不到。
    """

    # --- [新增] 软性循环限制逻辑 (Soft Limit) ---
    # 计算当前对话轮次中 Agent 调用工具的次数
    # 只要倒序遍历直到找到 HumanMessage (用户的最后一句话)
    current_turn_tool_calls = 0
    for msg in reversed(messages):
        if isinstance(msg, HumanMessage):
            break
        if isinstance(msg, AIMessage) and msg.tool_calls:
            current_turn_tool_calls += 1

    # 设置阈值：最多允许尝试 5 次搜索
    MAX_TOOL_RETRIES = 10

    if current_turn_tool_calls >= MAX_TOOL_RETRIES:
        # 强制停止：使用不带工具的原始 LLM 生成回复
        # 这样它就无法再调用 search_rules 了，只能说话
        force_stop_prompt = f"""
         [系统指令]：你已经连续进行了 {current_turn_tool_calls} 次检索，这已达到系统上限。
         请**立即停止搜索**，防止陷入死循环。
         请根据目前你已经检索到的信息（如果有），尝试回答用户的问题。
         如果完全没有找到相关信息，请直接礼貌地告知用户“在当前选定的规则书中未找到相关内容”，并建议用户尝试更换关键词或勾选更多规则书。
         """

        # 插入临时提示词
        input_messages = (
            [SystemMessage(content=base_system_prompt)]
            + messages
            + [SystemMessage(content=force_stop_prompt)]
        )

        # [关键] 调用 llm (原始模型) 而不是 llm_with_tools
        response = llm.invoke(input_messages)

        return {"messages": [response]}

    # --- [新增] 防死循环逻辑：分析历史搜索记录 ---

    previous_searches = []

    # 倒序遍历最近的 10 条消息，提取出 AI 已经用过的搜索词

    for msg in messages[-10:]:

        if isinstance(msg, AIMessage) and msg.tool_calls:

            for tc in msg.tool_calls:

                if tc["name"] == "search_rules":

                    q = tc["args"].get("query", "")

                    if q:
                        previous_searches.append(q)

    # 如果有过往搜索记录，把它们加入到 Prompt 里警告 Agent

    history_warning = ""

    if previous_searches:

        history_warning = f"""

    **严重警告 - 避免死循环**:

    你之前已经尝试过搜索这些关键词: {previous_searches}。

    **严禁**再次使用完全相同的关键词进行搜索！

    - 如果之前的搜索结果为空，说明该关键词无效。请必须更换**同义词**、**英文原名**或**更宽泛的概念**。

    - 如果你已经尝试了 3 次不同的搜索词仍然没有结果，请**立即停止搜索**，并诚实地告诉用户你在当前选定的规则书中找不到答案。

    """

    # 系统提示词 (System Prompt) - 这里的指令至关重要

    # 构造消息历史：SystemPrompt + HistoryWarning + ChatHistory

    messages = [SystemMessage(content=base_system_prompt + history_warning)] + state[
        "messages"
    ]

    # 调用 LLM

    response = llm_with_tools.invoke(messages)

    # 返回更新后的状态

    return {"messages": [response]}


# --- 4. 构建图 (Workflow) ---

workflow = StateGraph(AgentState)


# 添加节点

workflow.add_node("agent", reasoner)  # 思考节点

workflow.add_node("tools", ToolNode(tools))  # 工具执行节点 (LangGraph 自带)


# 添加边 (流程连线)

workflow.add_edge(START, "agent")  # 启动 -> 思考


# 添加条件边: 思考后去哪？

# 如果 LLM 决定调用工具 -> 去 "tools"

# 如果 LLM 决定直接说话 -> 结束 (END)

workflow.add_conditional_edges(
    "agent",
    tools_condition,
)


# 工具执行完后，把结果扔回给 agent 继续思考

workflow.add_edge("tools", "agent")


# 编译图 (MemorySaver 用于记住上下文)

graph = workflow.compile(checkpointer=MemorySaver())


if __name__ == "__main__":

    import uuid

    print("--- D&D Agent CLI 测试模式 ---")

    print("输入 'q' 退出。注意：本次测试默认只勾选了 ['PHB'] (玩家手册)")

    # 模拟一个线程 ID，用于测试记忆功能

    thread_id = str(uuid.uuid4())

    config = {"configurable": {"thread_id": thread_id}}

    # 模拟前端传入的参数

    mock_selected_books = ["核心规则"]

    while True:

        try:

            user_input = input("\nUser: ")

            if user_input.lower() in ["q", "quit", "exit"]:

                print("Bye!")

                break

            # 构造输入

            inputs = {
                "messages": [HumanMessage(content=user_input)],
                "selected_books": mock_selected_books,
            }

            print("\nThinking...", end="", flush=True)

            # 运行图并流式输出事件

            for event in graph.stream(inputs, config=config):

                for key, value in event.items():

                    if key == "agent":

                        # 获取 Agent 的最后一条消息

                        msg = value["messages"][-1]

                        if msg.tool_calls:

                            print(
                                f"\n[Agent] 决定查阅规则: {msg.tool_calls[0]['name']} args={msg.tool_calls[0]['args']}"
                            )

                        else:

                            print(f"\n[Agent] 回复: {msg.content}")

                    elif key == "tools":

                        # 获取工具的返回结果

                        msg = value["messages"][-1]

                        print(f"\n[Tool] 检索结果 (前100字符): {msg.content[:100]}...")

        except Exception as e:

            print(f"\nError: {e}")
