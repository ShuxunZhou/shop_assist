# 数据库查询工具

import pymysql
from config import MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASS, MYSQL_DB


def query_products(
    gender="male",
    category=None,
    limit=5
):
    conn = pymysql.connect(
        host=MYSQL_HOST,
        port=MYSQL_PORT,
        user=MYSQL_USER,
        password=MYSQL_PASS,
        database=MYSQL_DB,
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor
    )
    cursor = conn.cursor()

    sql = """
    SELECT
        p.name,
        p.category,
        s.price,
        s.currency
    FROM products p
    JOIN product_stock s ON p.id = s.product_id
    WHERE p.target_gender = %s
      AND s.in_stock = 1
    """

    params = [gender]

    if category:
        sql += " AND p.category = %s"
        params.append(category)

    sql += " ORDER BY s.price ASC LIMIT %s"
    params.append(limit)

    cursor.execute(sql, params)
    rows = cursor.fetchall()

    conn.close()
    return rows
