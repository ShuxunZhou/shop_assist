from langchain_core.tools import tool
import pymysql

from crawler.db import get_conn


@tool
def list_tables() -> str:
    """
    列出数据库中所有表及其注释
    """
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT table_name, table_comment
        FROM information_schema.tables
        WHERE table_schema = DATABASE();
    """)
    rows = cursor.fetchall()
    conn.close()

    return "\n".join(
        f"{r['table_name']}: {r['table_comment']}"
        for r in rows
    )

@tool
def describe_table(table_name: str) -> str:
    """
    查看指定表的字段结构
    """
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute(f"DESCRIBE {table_name}")
    rows = cursor.fetchall()
    conn.close()

    return "\n".join(
        f"{r['Field']} ({r['Type']})"
        for r in rows
    )

@tool
def execute_sql(sql: str) -> str:
    """
    执行只读 SQL 查询（SELECT）
    """
    if not sql.strip().lower().startswith("select"):
        return "❌ 只允许执行 SELECT 查询"

    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute(sql)
    rows = cursor.fetchall()
    conn.close()

    return str(rows[:10])  # 防止结果过大

@tool
def check_sql(sql: str) -> str:
    """
    检查 SQL 语法是否合法（不执行）
    """
    try:
        conn = get_conn()
        cursor = conn.cursor()
        cursor.execute(f"EXPLAIN {sql}")
        conn.close()
        return "✅ SQL 语法正确"
    except Exception as e:
        return f"❌ SQL 语法错误: {e}"

SYSTEM_PROMPT = """
你是一个数据库智能助手，负责将用户的自然语言需求转换为 SQL 查询。

工作规则：
1. 你不能直接假设表结构，必须先使用工具查看数据库。
2. 在写 SQL 前，必须：
   - 使用 list_tables
   - 使用 describe_table 查看相关表
3. 只允许生成 SELECT 查询。
4. 生成 SQL 后，必须先调用 check_sql。
5. 只有 SQL 通过检查，才能调用 execute_sql。
6. 查询结果用于向用户推荐商品。

数据库说明：
- products：商品基本信息（性别、类别、季节）
- product_stock：商品库存与价格信息
"""

from langchain.agents import create_tool_calling_agent, AgentExecutor
from llm import call_qwen

tools = [
    list_tables,
    describe_table,
    check_sql,
    execute_sql,
]

agent = create_tool_calling_agent(
    llm=call_qwen,
    tools=tools,
    system_prompt=SYSTEM_PROMPT,
)

agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
)


