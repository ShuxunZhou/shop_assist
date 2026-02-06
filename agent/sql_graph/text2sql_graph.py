# 定义工作流 -- > 来自MCP，异步
from contextlib import asynccontextmanager
from http.client import responses

from langchain_core.messages import AIMessage
from langchain_mcp_adapters.client import MultiServerMCPClient
import aiohttp
from langgraph.graph import StateGraph, MessagesState

from agent.sql_graph.llm_model import llm
from agent.sql_graph.my_state import SQLState
from agent.sql_graph.tools_node import generate_query_system_prompt

mcp_server_config = {
    "url" : "http://localhost:8000/sse",
    "transport": "sse",
}


# @asynccontextmanager 用于定义异步上下文管理器，可以在异步函数中使用“async with”语句来管理资源的获取和释放。
# 使得异步资源的获取和释放变得更加简洁和安全。
@asynccontextmanager #
async def make_graph():
    """定义并且编译工作流"""
    async with MultiServerMCPClient({'shuxun_mcp': mcp_server_config}) as client: # 创建一个多服务器MCP客户端
        tools = client.get_tools()

        # 查询所有表名列表的工具
        list_tables_tool = next(tool for tool in tools if tool.name == "list_tables_tool")
        # 执行SQL查询的工具
        db_query_tool = next(tool for tool in tools if tool.name == "db_query_tool")

        # 手动将前两个工具合并为一个节点：定义一个节点list_tables，参数必须是状态
        # 然后把这个拼凑出来的指令包装成一个AIMessage
        def list_tables(state: SQLState):
            """第一个节点"""
            tool_call = {
                "name": "list_tables_tool",
                "args": {},
                "id": "abc123",
                "type": "tool_call"
            }
            # 产生指令：
            tool_call_message = AIMessage(content="", tool_calls=[tool_call])
            # 调用工具：
            tool_message=list_tables_tool.invoke(tool_call)

            # 构造最终的响应消息,把所有表列表返回给用户
            response = AIMessage(f"所有可用的表: {tool_message.content}")

            return {"messages": [tool_call_message, tool_message, response]} # 返回状态}

        def generator_query(state: SQLState):
            # 第四个节点：生成 SQL 查询
            system_message = {
                "role": "system",
                "content": generate_query_system_prompt
            }
            llm_with_tool = llm.bind_tools([db_query_tool])
            resp = llm_with_tool.invoke([system_message] + state["messages"])
            return {"messages": [resp]}

        workflow = StateGraph(SQLState) # 得到工作流的编译器