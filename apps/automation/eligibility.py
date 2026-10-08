import json
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit


BASE_DIR = Path(__file__).resolve().parent
ANALYSIS_FILE = BASE_DIR / "data" / "analysis" / "latest.json"
COMMISSIONED_FILE = BASE_DIR / "data" / "affiliate" / "commissioned_products.json"
OUTPUT_FILE = BASE_DIR / "data" / "eligibility" / "latest.json"


def canonical_url(url):
    if not url:
        return None

    parts = urlsplit(str(url).strip())

    return urlunsplit((
        parts.scheme.lower(),
        parts.netloc.lower(),
        parts.path.rstrip("/"),
        "",
        ""
    ))


def load_json(path):
    if not path.exists():
        return None

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    analysis = load_json(ANALYSIS_FILE)

    if not analysis:
        print("ERROR: Analysis file not found.")
        print(f"Expected: {ANALYSIS_FILE}")
        return

    if not COMMISSIONED_FILE.exists():
        print("COMMISSIONED PRODUCT LIST NOT FOUND")
        print()
        print("Create this file first:")
        print(COMMISSIONED_FILE)
        print()
        print("Then add the Star Tech commissioned products.")
        return

    commissioned_data = load_json(COMMISSIONED_FILE)

    if not commissioned_data:
        print("ERROR: Commissioned product list is empty.")
        return

    if isinstance(commissioned_data, dict):
        commissioned_products = commissioned_data.get("products", [])
    else:
        commissioned_products = commissioned_data

    eligible_map = {}

    for item in commissioned_products:
        url = canonical_url(
            item.get("url")
            or item.get("product_url")
            or item.get("source_url")
            or item.get("tracking_url")
        )

        if not url:
            continue

        try:
            commission = float(
                str(
                    item.get("commission_rate")
                    or item.get("commission")
                    or item.get("rate")
                    or 0
                ).replace("%", "").strip()
            )
        except (ValueError, TypeError):
            commission = 0

        eligible_map[url] = {
            "commission_rate": commission,
            "commissioned": commission > 0,
            "product_name": item.get("product_name") or item.get("name"),
        }

    eligible_products = []

    for product in analysis.get("products", []):
        source_url = canonical_url(
            product.get("source_url") or product.get("url")
        )

        match = eligible_map.get(source_url)

        if not match:
            continue

        if match["commission_rate"] <= 0:
            continue

        product_copy = dict(product)
        product_copy["commission_rate"] = match["commission_rate"]
        product_copy["commissioned"] = True

        eligible_products.append(product_copy)

    eligible_products.sort(
        key=lambda x: x.get("score", 0),
        reverse=True
    )

    result = {
        "eligibility_status": "completed",
        "analysis_product_count": len(analysis.get("products", [])),
        "commissioned_product_count": len(commissioned_products),
        "eligible_product_count": len(eligible_products),
        "products": eligible_products,
    }

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print()
    print("=== AFFILIATE ELIGIBILITY ===")
    print(f"Analysis products: {len(analysis.get('products', []))}")
    print(f"Commissioned products: {len(commissioned_products)}")
    print(f"Eligible products: {len(eligible_products)}")

    if eligible_products:
        top = eligible_products[0]

        print()
        print("TOP ELIGIBLE PRODUCT:")
        print(f"Product: {top.get('product_name')}")
        print(f"Score: {top.get('score')}")
        print(f"Commission: {top.get('commission_rate')}%")

    print()
    print(f"Saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
