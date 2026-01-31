from typing import TypedDict, List
from langchain_core.messages import BaseMessage
from tools import query_products
from langchain_core.messages import AIMessage
from llm import call_qwen

class AgentState(TypedDict):
    messages: List[BaseMessage]
    products: list

# node 1: 判断是否要查询商品
def decide_node(state: AgentState):
    response = call_qwen(state["messages"])
    state["messages"].append(response)
    return state


# node 2: 查询数据库
def product_query_node(state: AgentState):
    products = query_products(gender="male", limit=5)
    state["products"] = products
    return state

# node 3: 根据查询结果生成回答
def recommend_node(state: AgentState):
    products = state.get("products", [])

    if not products:
        reply = "目前没有合适的商品可以推荐。"
    else:
        lines = [
            f"- {p['name']}（{p['category']}）：{p['price']} {p['currency']}"
            for p in products
        ]
        reply = "我为你推荐以下商品：\n" + "\n".join(lines)

    state["messages"].append(
        AIMessage(content=reply)
    )
    return state

from langgraph.graph import StateGraph, END

def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("decide", decide_node)
    graph.add_node("query_products", product_query_node)
    graph.add_node("recommend", recommend_node)

    graph.set_entry_point("decide")
    graph.add_edge("decide", "query_products")
    graph.add_edge("query_products", "recommend")
    graph.add_edge("recommend", END)

    return graph.compile()
