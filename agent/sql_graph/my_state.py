from typing import TypedDict, Annotated

from langchain_core.messages import AnyMessage
from langgraph.graph import add_messages


# 状态：存储工作流在执行过程中每个节点返回的数据
# 每个节点输出的数据大部分都是message【AIMessage, ToolMessage, HumanMessage】
class SQLState(TypedDict):
    # add_messages: 把每个节点输出的message添加到list中去
    messages: Annotated[list[AnyMessage], add_messages]
    # 状态中AddMessage除了list外的其他属性，后一个节点的输出内容是覆盖前一个节点的
    # user_id: int
    