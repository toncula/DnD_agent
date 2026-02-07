from typing import Annotated, Literal, TypedDict
from dotenv import load_dotenv
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[2]))

# 引入 Gemini 模型
from langchain_google_genai import ChatGoogleGenerativeAI

# 引入 LangGraph 组件
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.messages import HumanMessage, SystemMessage, AnyMessage
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


# --- 2. 初始化模型与工具 ---
tools = [search_rules]

llm = ChatGoogleGenerativeAI(
    model="gemini-3-flash-preview", temperature=0, max_retries=2  # 规则问题不需要太发散
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

    # 系统提示词 (System Prompt) - 这里的指令至关重要
    system_prompt = f"""你是一个精通 D&D 5E (龙与地下城) 中文规则的地下城主(DM)助手。
    
    **当前环境限制**:
    用户仅允许你参考以下规则书: {books if books else '所有可用规则书'}。
    
    **你的行动准则**:
    1. **必须查书**: 遇到规则问题，必须调用 `search_rules` 工具检索，严禁仅凭记忆或臆造回答。
    2. **参数传递**: 调用工具时，必须将上面的规则书列表准确传递给 `book_filter` 参数。
    3. **具体胜过一般**: 如果检索结果中，职业特性/专长描述与通用战斗规则冲突，以具体的特性为准 (Specific Beats General)。
    4. **引用来源**: 回答必须注明信息来源（例如：根据《玩家手册》第x章...）。
    5. **诚实**: 如果查不到，就说查不到。
    """

    # 构造消息历史：SystemPrompt + ChatHistory
    messages = [SystemMessage(content=system_prompt)] + state["messages"]

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
