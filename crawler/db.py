import pymysql
from datetime import datetime
from config import MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASS, MYSQL_DB

BRAND_ID = 1   # Arc'teryx


def get_conn():
    return pymysql.connect(
        host=MYSQL_HOST,
        port=MYSQL_PORT,
        user=MYSQL_USER,
        password=MYSQL_PASS,
        database=MYSQL_DB,
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True
    )


def upsert_product(cursor, product):
    """
    products 表：用 sku 去重
    """
    cursor.execute(
        "SELECT id FROM products WHERE sku = %s",
        (product["sku"],)
    )
    row = cursor.fetchone()
    if row:
        return row["id"]

    sql = """
    INSERT INTO products
    (brand_id, sku, name, category, season, material, target_gender, product_url)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """
    cursor.execute(sql, (
        BRAND_ID,
        product["sku"],
        product["name"],
        product["category"],
        product["season"],
        product["material"],
        product["target_gender"],
        product["product_url"]
    ))
    return cursor.lastrowid


def upsert_stock(cursor, product_id, stock):
    sql = """
    INSERT INTO product_stock
    (product_id, price, currency, in_stock, available_sizes, last_checked)
    VALUES (%s, %s, %s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE
        price = VALUES(price),
        in_stock = VALUES(in_stock),
        last_checked = VALUES(last_checked)
    """
    cursor.execute(sql, (
        product_id,
        stock["price"],
        stock["currency"],
        stock["in_stock"],
        stock["available_sizes"],
        stock["last_checked"]
    ))
