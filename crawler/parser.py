from datetime import datetime


def infer_category(name: str):
    name = name.lower()
    if "jacket" in name or "parka" in name or "coat" in name:
        return "jacket"
    if "hoody" in name or "hoodie" in name:
        return "hoodie"
    if "pant" in name or "trouser" in name:
        return "pants"
    if "shoe" in name:
        return "shoes"
    if "hat" in name or "cap" in name or "toque" in name:
        return "accessory"
    return "other"


def infer_season(category: str):
    if category == "jacket":
        return "winter"
    if category == "hoodie":
        return "autumn"
    return "all"


def parse_item(item: dict):
    """
    GraphQL item JSON → product + stock
    """
    name = item.get("name")
    sku = item.get("sku")

    price_info = item["price_range"]["minimum_price"]

    final_price = price_info["final_price"]["value"]
    currency = price_info["final_price"]["currency"]
    regular_price = price_info["regular_price"]["value"]
    discount = price_info.get("discount")

    category = infer_category(name)
    season = infer_season(category)

    product = {
        "sku": sku,
        "name": name,
        "category": category,
        "season": season,
        "material": None,
        "target_gender": "male",
        "product_url": f"https://outlet.arcteryx.com/us/en/shop/{sku}"
    }

    stock = {
        "price": final_price,
        "currency": currency,
        "in_stock": True,
        "available_sizes": None,
        "last_checked": datetime.now(),
        "regular_price": regular_price,
        "discount": discount
    }

    return product, stock
