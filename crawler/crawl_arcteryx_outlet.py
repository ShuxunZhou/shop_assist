import pymysql
from db import get_conn, upsert_product, upsert_stock
from parser import parse_item
from config import MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASS, MYSQL_DB
from playwright.sync_api import sync_playwright

seen_skus = set()
BRAND_ID = 1   # Arc'teryx 在 brands 表中的 id

TARGET_PAGES = [
    {
        "url": "https://outlet.arcteryx.com/us/en/c/mens/",
        "gender": "male"
    },
    {
        "url": "https://outlet.arcteryx.com/us/en/c/womens/",
        "gender": "female"
    }
]



# =====================================================
# MySQL 连接
# =====================================================
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


# =====================================================
# 简单规则：category / season
# =====================================================
def infer_category(name: str):
    name = name.lower()
    if "jacket" in name or "parka" in name or "coat" in name:
        return "jacket"
    if "hoody" in name or "hoodie" in name:
        return "hoodie"
    if "pant" in name or "trouser" in name:
        return "pants"
    return "other"


def infer_season(category: str):
    if category == "jacket":
        return "winter"
    if category == "hoodie":
        return "autumn"
    return "all"


# =====================================================
# products 表：upsert
# =====================================================
def upsert_product(cursor, product):
    cursor.execute(
        "SELECT id FROM products WHERE product_url = %s AND target_gender = %s",
        (product["product_url"], product["target_gender"])
    )

    row = cursor.fetchone()
    if row:
        return row["id"]

    sql = """
    INSERT INTO products
    (brand_id, name, category, season, material, target_gender, product_url)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    cursor.execute(sql, (
        BRAND_ID,
        product["name"],
        product["category"],
        product["season"],
        product["material"],
        product["target_gender"],
        product["product_url"]
    ))
    return cursor.lastrowid


# =====================================================
# product_stock 表：upsert
# =====================================================
def upsert_stock(cursor, product_id, stock):
    sql = """
    INSERT INTO product_stock
    (product_id, price, currency, in_stock, available_sizes, last_checked)
    VALUES (%s, %s, %s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE
        price = VALUES(price),
        in_stock = VALUES(in_stock),
        available_sizes = VALUES(available_sizes),
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


# =====================================================
# 主爬虫逻辑（监听接口）
# =====================================================
seen_products = set()  # 根据 gender + sku 去重

def crawl(target_url: str, gender: str):
    conn = get_conn()
    cursor = conn.cursor()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        def handle_response(response):
            try:
                url = response.url

                # 🎯 只处理 Arc'teryx 商品价格 GraphQL 接口
                if "api/mcgql" not in url:
                    return
                if "gqlGetProductsPricesBySku" not in url:
                    return

                data = response.json()

                items = (
                    data
                    .get("data", {})
                    .get("products", {})
                    .get("items", [])
                )

                if not items:
                    return

                print(f"\n🎯 捕获商品接口（{len(items)} items）")

                # sku + gender 去重
                for item in items:
                    try:
                        sku = item.get("sku")
                        if not sku:
                            continue
                        key = (sku, gender)
                        if key in seen_products:
                            continue

                        seen_products.add(key)

                        # =========================
                        # 1️⃣ JSON → 结构化数据
                        # =========================
                        product, stock = parse_item(item)
                        product["target_gender"] = gender

                        # =========================
                        # 2️⃣ 写入 MySQL
                        # =========================
                        product_id = upsert_product(cursor, product)
                        upsert_stock(cursor, product_id, stock)

                        # =========================
                        # 3️⃣ 控制台确认
                        # =========================
                        print("===================================")
                        print(f"✔ 已入库")
                        print(f"Name          : {product['name']}")
                        print(f"SKU           : {product['sku']}")
                        print(f"Final Price   : {stock['price']} {stock['currency']}")
                        print("===================================")

                    except Exception as item_err:
                        print(f"❌ item parse/db error (sku={item.get('sku')}):", item_err)

            except Exception as e:
                print("❌ response parse error:", e)

        # 监听网络响应
        page.on("response", handle_response)

        print("🚀 打开页面")
        page.goto(target_url, timeout=30000)

        # 👇 触发懒加载
        for _ in range(6):
            page.mouse.wheel(0, 2000)
            page.wait_for_timeout(2000)

        print("⌛ 等待接口返回完成")
        page.wait_for_timeout(5000)

        browser.close()
    conn.close()


# =====================================================
if __name__ == "__main__":
    if __name__ == "__main__":
        for page in TARGET_PAGES:
            crawl(page["url"], page["gender"])

        print("\n===================================")
        print(f"🎉 本次共爬取商品数（SKU + gender）：{len(seen_products)}")
        print("===================================")
