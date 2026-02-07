# 定义工作流 -- > 来自MCP，异步
from contextlib import asynccontextmanager
from http.client import responses
from typing import Literal

from langchain_core.messages import AIMessage
from langchain_mcp_adapters.client import MultiServerMCPClient
import aiohttp
from langgraph.constants import START, END
from langgraph.graph import StateGraph, MessagesState
from langgraph.prebuilt import ToolNode

from agent.sql_graph.llm_model import llm
from agent.sql_graph.my_state import SQLState
from agent.sql_graph.tools_node import generate_query_system_prompt, query_check_system, call_get_schema, \
    get_schema_node

mcp_server_config = {
    "url" : "http://localhost:8000/sse",
    "transport": "sse",
}

# @asynccontextmanager 用于定义异步上下文管理器，可以在异步函数中使用“async with”语句来管理资源的获取和释放。
# 使得异步资源的获取和释放变得更加简洁和安全。
# @asynccontextmanager
async def make_graph():
    """定义并且编译工作流"""
    # async 在 langchain-mcp-adapters >= 0.1.0 改了 API 设计
    # async with MultiServerMCPClient({'shuxun_mcp': mcp_server_config}) as client: # 创建一个多服务器MCP客户端
        # tools = client.get_tools()

    client = MultiServerMCPClient({'shuxun_mcp': mcp_server_config})
    tools = await client.get_tools() # 获取工具列表（异步）

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
        # 这里需要把工具绑定到 llm 上，才能在系统提示词中调用工具（但是不强制工具调用，允许模型在获得解决方案时自然响应）
        llm_with_tool = llm.bind_tools([db_query_tool])
        resp = llm_with_tool.invoke([system_message] + state["messages"])
        return {"messages": [resp]}

    def check_query(state: SQLState):
        # 第五个节点：检查 SQL 语法，并且要执行一下这个SQL语句，检查是否有错误
        system_message = {
            "role": "system",
            "content": query_check_system
        }
        tool_call = state["messages"][-1].tool_calls[0]
        # 得到生成后的SQL语句
        user_message = {"role": "user", "content": tool_call["args"]["query"]}
        llm_with_tool = llm.bind_tools([db_query_tool], tool_choice='any') # 强制调用工具

        response = llm_with_tool.invoke([system_message, user_message])
        response.id = state["messages"][-1].id # 保持消息ID不变，方便后续工具调用

        return {"messages": [response]}

    # 第六个节点：执行 SQL 查询
    run_query_node = ToolNode([db_query_tool], name="run_query")

    # 第四个节点后定义动态路由
    def should_continue(state: SQLState) -> Literal[END, "check_query"]:
        """条件路由的动态边， 根据上一个节点的输出动态决定下一步执行哪个节点"""
        messages = state["messages"]
        last_message = messages[-1]
        if not last_message.tool_calls:  # 如果没有工具调用，说明SQL语法检查通过了
            return END
        else:
            return "check_query"

    workflow = StateGraph(SQLState) # 得到工作流的编译器
    # 函数本身就是节点，因此不用再加括号
    workflow.add_node(list_tables)
    workflow.add_node(call_get_schema)
    workflow.add_node(get_schema_node)
    workflow.add_node(generator_query)
    workflow.add_node(check_query)
    workflow.add_node(run_query_node)

    workflow.add_edge(START, "list_tables")
    workflow.add_edge("list_tables", "call_get_schema")
    workflow.add_edge("call_get_schema", "call_get_schema")
    workflow.add_edge("call_get_schema", "generator_query")
    workflow.add_conditional_edges('generator_query', should_continue)
    workflow.add_edge("check_query", "run_query")
    workflow.add_edge("run_query", "generator_query")

    graph = workflow.compile() # 编译工作流
    return graph #异步环境，yield返回
