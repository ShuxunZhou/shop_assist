from typing import List, Optional
import pymysql

from config import (
    MYSQL_HOST,
    MYSQL_PORT,
    MYSQL_USER,
    MYSQL_PASS,
    MYSQL_DB,
)


class MySQLDatabaseManager:
    """
    MySQL 数据库管理器（只读）
    仅提供 schema 查询与 SELECT 执行能力
    """

    def __init__(self):
        self._conn_params = dict(
            host=MYSQL_HOST,
            port=MYSQL_PORT,
            user=MYSQL_USER,
            password=MYSQL_PASS,
            database=MYSQL_DB,
            charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=True,
        )

    # =====================================================
    # 内部工具：获取连接
    # =====================================================
    def _get_conn(self):
        return pymysql.connect(**self._conn_params)

    # =====================================================
    # Tool 1 支持：获取所有表及描述信息
    # =====================================================
    def get_tables(self) -> str:
        """
        获取当前数据库中所有表及其描述信息
        """
        sql = """
        SELECT
            table_name,
            table_comment
        FROM information_schema.tables
        WHERE table_schema = DATABASE();
        """

        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute(sql)
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            return "No tables found."

        return "\n".join(
            f"{r['table_name']} - {r['table_comment'] or 'no comment'}"
            for r in rows
        )

    # =====================================================
    # Tool 2 支持：获取表结构信息
    # =====================================================
    def get_table_schema(
        self,
        table_names: Optional[List[str]] = None
    ) -> str:
        """
        获取指定表（或所有表）的结构信息
        """
        conn = self._get_conn()
        cursor = conn.cursor()

        if table_names:
            tables = table_names
        else:
            cursor.execute("SHOW TABLES")
            tables = [list(row.values())[0] for row in cursor.fetchall()]

        schema_lines = []

        for table in tables:
            cursor.execute(f"DESCRIBE {table}")
            rows = cursor.fetchall()

            schema_lines.append(f"\nTable `{table}`:")
            for r in rows:
                schema_lines.append(
                    f"  - {r['Field']} ({r['Type']})"
                )

        conn.close()
        return "\n".join(schema_lines)

    # =====================================================
    # Tool 3 支持：执行 SELECT 查询
    # =====================================================
    def execute_select(self, sql: str) -> List[dict]:
        """
        执行 SELECT 查询并返回结果
        """
        if not sql.strip().lower().startswith("select"):
            raise ValueError("Only SELECT statements are allowed.")

        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute(sql)
        rows = cursor.fetchall()
        conn.close()

        return rows

    # =====================================================
    # Tool 4 支持：SQL 语法检查
    # =====================================================
    def explain_sql(self, sql: str) -> str:
        """
        使用 EXPLAIN 检查 SQL 语法是否合法
        """
        if not sql.strip().lower().startswith("select"):
            raise ValueError("Only SELECT statements are allowed.")

        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute(f"EXPLAIN {sql}")
        conn.close()

        return "✅ SQL syntax is valid."
