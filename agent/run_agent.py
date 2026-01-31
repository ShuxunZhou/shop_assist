from langchain_core.messages import HumanMessage
from graph import build_graph

graph = build_graph()

if __name__ == "__main__":
    state = {
        "messages": [],
        "products": []
    }

    while True:
        user_input = input("\n🧑 用户：")
        if user_input.lower() in ["exit", "quit"]:
            break

        state["messages"].append(
            HumanMessage(content=user_input)
        )

        state = graph.invoke(state)

        print("\n🤖 Agent：", state["messages"][-1].content)
