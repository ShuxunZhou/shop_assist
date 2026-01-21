from crawler import fetch_products
from parser import normalize
from crawler.db import get_conn, upsert_product, upsert_stock

URL = "https://example.com/jackets"

def run():
    conn = get_conn()
    brand_id = 1  # 假设 Uniqlo

    raw_products = fetch_products(URL)

    for p in raw_products:
        data = normalize(p)
        pid = upsert_product(conn, brand_id, data)
        upsert_stock(conn, pid, data)

    conn.close()

if __name__ == "__main__":
    run()
