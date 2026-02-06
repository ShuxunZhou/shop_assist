from langchain_community.utilities import SQLDatabase
from mcp.server import FastMCP
from agent.sql_graph.llm_model import zhipuai_client

mcp_server = FastMCP(name="shuxun-mcp", instructions='我自己的MCP服务', port=8000)
db = SQLDatabase.from_uri(
        'mysql+pymysql://root:1234@localhost:3306/shop_assist'
    )

@mcp_server.tool('my_search_tool', description='专门搜索互联网中的内容')
def my_search(query: str) -> str:
    """搜索互联网上的内容"""
    try:
        response = zhipuai_client.web_search.web_search(
            search_engine='search-std',
            search_query=query
        )
        print(response)
        if response.search_result:
            return "\n\n".join([d.content for d in response.search_result])
    except Exception as e:
        print(e)
        return '没有搜索到任何内容！'



@mcp_server.tool('list_tables_tool', description='输入一个空的字符串，输出的是数据库中所有的表名，表名用逗号分隔')
def list_tables_tool(query: str) -> str:
    """输入一个空的字符串，输出的是数据库中所有的表名，表名用逗号分隔"""
    return ", ".join(db.get_usable_table_names())


@mcp_server.tool()
def db_query_tool(query: str) -> str:
    """
    执行SQL查询，返回查询结果。
    如果查询不正确，则返回错误信息。
    如果返回错误，请重写查询语句，检查后重试。

    Args:
        query (str):  要执行的SQL查询语句

    Returns:
        str: 查询结果或错误信息
    """
    result = db.run_no_throw(query) # 执行查询（不抛异常）
    if not result:
        return "查询没有返回任何结果，或者查询语句有误，请检查后重试。"
    return result