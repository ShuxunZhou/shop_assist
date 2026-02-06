# 执行工作流

from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langgraph.graph import MessagesState
from sqlalchemy.sql.annotation import Annotated

from agent.sql_graph.llm_model import llm

# 状态：存储工作流在执行过程中每个节点返回的数据
# class MyState(TypedDict):
#     messages: Annotated[list, add_messages]



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
    pass