import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage
from langgraph.graph import StateGraph
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver
from app.state import AgentState
from app.tools import ALL_TOOLS

load_dotenv()
SYSTEM_PROMPT = """You are GroceryBot — a smart personal grocery assistant.

You help users track and analyze their monthly grocery spending.

You have these tools:
  1. get_all_slips_summary → overview of all slips
  2. get_item_price_history → price history of any item
  3. compare_two_months_tool → compare 2 months spending
  4. get_spending_trend → monthly spending trend
  5. calculator → math operations
  6. search_market_price → live market prices online

Rules:
  - Always use user_id from context when calling tools
  - Use Rs. for Pakistani Rupees
  - Be friendly, clear and specific with numbers
  - Always use calculator tool for math — never calculate mentally
  - When user asks about an item → use get_item_price_history
  - When comparing months → use compare_two_months_tool
  - When asking about trends → use get_spending_trend
  - When asking today price → use search_market_price
  - If no slips found → tell user to upload slip photos first
  - Greet user by name when starting conversation"""

def build_graph():
    groq_key = os.getenv("GROQ_API_KEY")
    if not groq_key:
        raise ValueError(
            "GROQ_API_KEY not found!\n"
            "Get free key at: https://console.groq.com\n"
        )
    llm = ChatGroq(
        model = "meta-llama/llama-4-scout-17b-16e-instruct", 
        api_key = groq_key,
        temperature = 0,
    ).bind_tools(ALL_TOOLS)
    
    def llm_node(state: AgentState):
        """Think and decide which tool to call or give final answer."""
        system = SystemMessage(
            content=(
                f"{SYSTEM_PROMPT}\n\n"
                f"Current user_id : {state.get('user_id', 1)}\n"
                f"Current user name: {state.get('user_name', 'User')}"
            )
        )
        messages = [system] + state["messages"]
        response = llm.invoke(messages)
        return {"messages": [response]}

    builder = StateGraph(AgentState)
    builder.add_node("llm", llm_node)
    builder.add_node("tools", ToolNode(ALL_TOOLS))

    builder.set_entry_point("llm")
    builder.add_conditional_edges("llm", tools_condition)

    builder.add_edge("tools", "llm")
    checkpointer = MemorySaver()

    return builder.compile(checkpointer=checkpointer)
  #test
if __name__ == "__main__":
    print("Testing Groq connection...")
    try:
        groq_key = os.getenv("GROQ_API_KEY")
        if not groq_key:
            print("GROQ_API_KEY not found in .env")
            print(" Get free key at: https://console.groq.com")
            exit(1)

        llm = ChatGroq(
            model = "meta-llama/llama-4-scout-17b-16e-instruct",
            api_key = groq_key,
        )
        response = llm.invoke("Say hello in one sentence")
        print(f" Groq working: {response.content}")
        print("\nBuilding graph...")
        graph = build_graph()
        print(" Graph built successfully!")
        print("\n Everything is ready!")

    except Exception as e:
        print(f" Error: {e}")
        print("\nMake sure:")
        print(" 1. GROQ_API_KEY is in .env file")
        print(" 2. pip install langchain-groq")
