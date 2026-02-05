from typing import Optional, List
from langchain_core.tools import BaseTool
from pydantic import create_model

from db.mysql_manager import MySQLDatabaseManager



# =====================================================
# Tool 1：获取所有表及描述信息
# =====================================================
class ListTablesTool(BaseTool):
    """
    获取数据库中所有表及其描述信息
    """

    name: str = "sql_db_tables"
    description: str = (
        "获取当前 MySQL 数据库中的所有表名及其描述信息。"
        "在编写 SQL 之前，应首先调用此工具了解数据库结构。"
    )

    db_manager: MySQLDatabaseManager

    def __init__(self, db_manager: MySQLDatabaseManager, **kwargs):
        super().__init__(**kwargs)
        self.db_manager = db_manager

        # 无参数工具，也要显式声明 args_schema
        self.args_schema = create_model(
            "ListTablesToolArgs"
        )

    def _run(self) -> str:
        return self.db_manager.get_tables()


# =====================================================
# Tool 2：获取表结构信息
# =====================================================
class TableSchemaTool(BaseTool):
    """
    获取指定表的结构信息
    """

    name: str = "sql_db_schema"
    description: str = (
        "获取 MySQL 数据库中指定表的详细结构信息，"
        "包括字段名、字段类型、主键等。"
        "参数 table_names 为表名列表。"
    )

    db_manager: MySQLDatabaseManager

    def __init__(self, db_manager: MySQLDatabaseManager, **kwargs):
        super().__init__(**kwargs)
        self.db_manager = db_manager

        self.args_schema = create_model(
            "TableSchemaToolArgs",
            table_names=(Optional[List[str]], None),
        )

    def _run(
        self,
        table_names: Optional[List[str]] = None
    ) -> str:
        return self.db_manager.get_table_schema(table_names)


# =====================================================
# Tool 3：执行 SQL 查询（只允许 SELECT）
# =====================================================
class ExecuteSQLTool(BaseTool):
    """
    执行 SQL 查询工具（只读）
    """
    name: str = "sql_db_query"
    description: str = (
        "执行一条 SQL SELECT 查询并返回结果。"
        "只能用于 SELECT 查询，不允许 INSERT / UPDATE / DELETE。"
        "在执行前应先使用 sql_db_check 工具检查 SQL。"
    )

    db_manager: MySQLDatabaseManager

    def __init__(self, db_manager: MySQLDatabaseManager, **kwargs):
        super().__init__(**kwargs)
        self.db_manager = db_manager

        self.args_schema = create_model(
            "ExecuteSQLToolArgs",
            sql=(str, ...),
        )

    def _run(self, sql: str) -> str:
        # 二次防护（即使 LLM 犯错）
        if not sql.strip().lower().startswith("select"):
            return "❌ Only SELECT statements are allowed."

        results = self.db_manager.execute_select(sql)

        if not results:
            return "No results found."

        # 防止返回过多内容
        return str(results[:10])


# =====================================================
# Tool 4：检查 SQL 查询语法
# =====================================================
class CheckSQLTool(BaseTool):
    """
    SQL 语法检查工具
    """

    name: str = "sql_db_check"
    description: str = (
        "检查一条 SQL 查询的语法是否合法，但不会真正执行该查询。"
        "通常应在执行 SQL 之前调用此工具。"
    )

    db_manager: MySQLDatabaseManager

    def __init__(self, db_manager: MySQLDatabaseManager, **kwargs):
        super().__init__(**kwargs)
        self.db_manager = db_manager

        self.args_schema = create_model(
            "CheckSQLToolArgs",
            sql=(str, ...),
        )

    def _run(self, sql: str) -> str:
        if not sql.strip().lower().startswith("select"):
            return "❌ Only SELECT statements are allowed."

        try:
            return self.db_manager.explain_sql(sql)
        except Exception as e:
            return f"❌ SQL syntax error: {e}"
