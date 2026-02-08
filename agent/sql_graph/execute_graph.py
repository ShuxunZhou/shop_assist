import os
import ssl
import certifi
# 由于在某些环境中，SSL证书可能会导致HTTPS请求失败，因此使用certifi库来提供一个可靠的证书颁发机构列表，并将其配置为默认的HTTPS上下文。
os.environ["SSL_CERT_FILE"] = certifi.where()
ssl._create_default_https_context = ssl.create_default_context(
    cafile=certifi.where()
)

# 执行工作流
import asyncio

from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langgraph.graph import MessagesState
from sqlalchemy.sql.annotation import Annotated

from agent.sql_graph.draw_png import draw_graph
from agent.sql_graph.llm_model import llm
from agent.sql_graph.text2sql_graph import make_graph


# 状态：存储工作流在执行过程中每个节点返回的数据
# class MyState(TypedDict):
#     messages: Annotated[list, add_messages]

async def execute_graph():
    # 在异步环境下执行工作流
    async with make_graph() as graph:
        draw_graph(graph, 'text2sql.png')
        while True:
            user_input = input("用户：")
            if user_input.lower() in ["q", "quit", "exit"]:
                print("对话结束，拜拜！")
                break
            else:
                async for event in graph.astream({"messages":[{"role": "user", "content": user_input}]}, stream_mode="values"):
                    event["messages"][-1].pretty_print()


if __name__ == '__main__':
#     db = SQLDatabase.from_uri(
#         'mysql+pymysql://root:1234@localhost:3306/shop_assist'
#     )
#     toolkit = SQLDatabaseToolkit(db=db, llm=llm)
#
#     # 得到所有工具
#     tools = toolkit.get_tools()
#     for tool in tools:
#         print(f"Tool name: {tool.name}")
#         print(f"Tool description: {tool.description}\n")
#
#     # 需要用到langchain提供的 sql_db_list_tables 获取所有表名
#     # next() 用法：从可迭代对象中获取第一个符合条件的元素
#     list_tables_tool = next(tool for tool in tools if tool.name == "sql_db_list_tables")
#
#     print(list_tables_tool.invoke(""))

    asyncio.run(execute_graph())