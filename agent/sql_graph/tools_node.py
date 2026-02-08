from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_community.utilities import SQLDatabase
from langgraph.prebuilt import ToolNode

from agent.sql_graph.llm_model import llm
from agent.sql_graph.my_state import SQLState

db = SQLDatabase.from_uri(
        'mysql+pymysql://root:1234@localhost:3306/shop_assist'
    )
toolkit = SQLDatabaseToolkit(db=db, llm=llm)
tools = toolkit.get_tools()

# 需要用到langchain提供的 sql_db_list_tables 获取所有表名
get_schema_tool = next(tool for tool in tools if tool.name == "sql_db_schema")
# print(get_schema_tool.invoke('products'))

# 第三个节点：获取数据库 schema 信息
def call_get_schema(state: SQLState):
    # 注意：Langchain强制要求所有模型都接受 tool_choice='any'
    # 以及  tool_choice=<工具名称字符串> 两种参数
    llm_with_tools = llm.bind_tools([get_schema_tool], tool_choice='any')
    # 调用完工具得到一个指令（不是真正调用工具）
    response = llm_with_tools.invoke(state["messages"])
    return {"messages": [response]}

# 第四个节点：直接采用langgraph提供的ToolNode，执行 get_schema_tool 工具
get_schema_node = ToolNode([get_schema_tool], name="get_schema")

# 下方保存提示词模板：
# 节点5：生成 SQL 查询的系统提示词模板
generate_query_system_prompt = """
你是一个设计用于与SQL数据库交互的智能体。
给顶一个输入问题，创建一个语法正确的{dialect}查询来运行，
然后查看查询结果并返回答案。除非用户明确指定他们希望获取的示例数量，
否则始终将查询限制为最多{top_k}条结果。

你可以按相关列对结果进行排序，以返回数据库中最有趣的示例。
永远不要查询特定表的所有列，只查询与问题相关的列

不要对数据库进行任何DML语句(INSERT, UPDATE, DELETE)或DDL语句(CREATE, DROP, ALTER)。
""".format(
    dialect=db.dialect,
    top_k=5
)

# 节点6：检查 SQL 语法的系统提示词模板
query_check_system = """
你是一个SQL语法检查助手，负责检查用户生成的SQL查询语句是否符合SQL语法规范。
请仔细检查SQLite查询中的常见错误，包括：
- Using NOT IN with NULL values
- Using UNION when UNION ALL should have been used
- Using BETWEEN for exclusive ranges
- Data type mismatch in predicates
- Properly quoting identifiers
- Using the correct number of arguments for functions
- Casting to the correct data type
- Using the proper columns for joins

如果发现上述任何错误，请重写查询。如果没有错误，请原样返回查询语句。

检查完成后，你将调用适当的工具来执行查询。
"""