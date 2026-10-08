import json
import re
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
RESEARCH_FILE = BASE_DIR / "data" / "research" / "latest.json"
OUTPUT_DIR = BASE_DIR / "data" / "analysis"
OUTPUT_FILE = OUTPUT_DIR / "latest.json"


EXCLUDED_KEYWORDS = [
    "warranty",
    "refund",
    "return-policy",
    "privacy-policy",
    "terms",
    "information",
    "offer",
    "happy-hour",
    "pc_builder",
]


def clean_text(value):
    if value is None:
        return ""

    text = str(value)

    replacements = {
        "à§³": "৳",
        "â€‘": "-",
        "â€“": "-",
        "â€”": "-",
        "Â": "",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    return " ".join(text.split())


def extract_number(value):
    if value is None:
        return None

    text = clean_text(value)
    numbers = re.findall(r"\d+(?:,\d+)*(?:\.\d+)?", text)

    if not numbers:
        return None

    try:
        return float(numbers[0].replace(",", ""))
    except ValueError:
        return None


def get_price(product):
    price = extract_number(product.get("price"))

    if price is not None:
        return price

    specs = product.get("specifications", {})
    return extract_number(specs.get("Price"))


def get_old_price(product):
    old_price = extract_number(product.get("old_price"))

    if old_price is not None:
        return old_price

    specs = product.get("specifications", {})
    price_text = clean_text(specs.get("Price"))

    numbers = re.findall(r"\d+(?:,\d+)*(?:\.\d+)?", price_text)

    if len(numbers) >= 2:
        try:
            return float(numbers[1].replace(",", ""))
        except ValueError:
            pass

    return None


def calculate_discount(price, old_price):
    if not price or not old_price or old_price <= price:
        return 0

    return round(((old_price - price) / old_price) * 100, 2)


def get_spec_text(product):
    specs = product.get("specifications", {})

    return clean_text(
        " ".join(
            f"{key} {value}"
            for key, value in specs.items()
        )
    ).lower()


def score_product(product):
    title = clean_text(product.get("title"))
    description = clean_text(product.get("description"))
    brand = clean_text(product.get("brand"))
    category = clean_text(product.get("category"))
    url = clean_text(product.get("source_url"))
    specs = get_spec_text(product)

    combined = (
        f"{title} {description} {brand} "
        f"{category} {specs}"
    ).lower()

    price = get_price(product)
    old_price = get_old_price(product)
    discount = calculate_discount(price, old_price)

    score = 0
    reasons = []

    # -------------------------------------------------
    # 1. Price / affordability: 20 points
    # -------------------------------------------------

    if price is not None:
        if 30000 <= price <= 80000:
            score += 20
            reasons.append("Strong mainstream price range")
        elif 20000 <= price < 30000:
            score += 17
            reasons.append("Highly affordable price")
        elif 80000 < price <= 120000:
            score += 15
            reasons.append("Premium but still marketable price")
        elif price < 20000:
            score += 12
            reasons.append("Very low price")
        elif price <= 160000:
            score += 10
            reasons.append("High-ticket product")
        else:
            score += 6
            reasons.append("Very high price")

    # -------------------------------------------------
    # 2. Discount: 15 points
    # -------------------------------------------------

    if discount >= 20:
        score += 15
        reasons.append("Very strong discount")
    elif discount >= 10:
        score += 12
        reasons.append("Strong discount")
    elif discount >= 5:
        score += 8
        reasons.append("Moderate discount")
    elif discount > 0:
        score += 5
        reasons.append("Discount available")

    # -------------------------------------------------
    # 3. Performance / specification: 20 points
    # -------------------------------------------------

    performance_terms = [
        "core i5",
        "core i7",
        "core ultra",
        "ryzen 5",
        "ryzen 7",
        "ryzen ai",
        "m1",
        "m2",
        "m3",
        "m4",
        "m5",
        "16gb",
        "32gb",
        "512gb",
        "1tb",
        "rtx",
    ]

    performance_hits = sum(
        1 for term in performance_terms
        if term in combined
    )

    performance_score = min(performance_hits * 3, 20)
    score += performance_score

    if performance_score >= 12:
        reasons.append("Strong performance specifications")
    elif performance_score >= 6:
        reasons.append("Good performance specifications")

    # -------------------------------------------------
    # 4. Bangladesh market suitability: 15 points
    # -------------------------------------------------

    market_terms = [
        "laptop",
        "fhd",
        "ssd",
        "8gb",
        "16gb",
        "intel",
        "amd",
        "ryzen",
        "apple",
        "lenovo",
        "hp",
        "dell",
        "acer",
        "asus",
        "msi",
    ]

    market_hits = sum(
        1 for term in market_terms
        if term in combined
    )

    market_score = min(market_hits * 2, 15)
    score += market_score

    if market_score >= 10:
        reasons.append("Strong Bangladesh-market relevance")

    # -------------------------------------------------
    # 5. Purchase intent: 10 points
    # -------------------------------------------------

    intent_terms = [
        "in stock",
        "fhd",
        "ssd",
        "ram",
        "processor",
        "laptop",
        "price",
        "order online",
    ]

    intent_hits = sum(
        1 for term in intent_terms
        if term in combined
    )

    intent_score = min(intent_hits * 2, 10)
    score += intent_score

    if intent_score >= 6:
        reasons.append("High purchase-intent signals")

    # -------------------------------------------------
    # 6. Social media marketing potential: 10 points
    # -------------------------------------------------

    social_terms = [
        "gaming",
        "macbook",
        "apple",
        "ai",
        "oled",
        "touch",
        "ultra",
        "rtx",
        "ryzen 7",
        "core i7",
        "core ultra",
        "16gb",
    ]

    social_hits = sum(
        1 for term in social_terms
        if term in combined
    )

    social_score = min(social_hits * 2, 10)
    score += social_score

    if social_score >= 6:
        reasons.append("Strong social-media marketing potential")

    # -------------------------------------------------
    # 7. Affiliate potential: 10 points
    # -------------------------------------------------

    if price is not None:
        if 40000 <= price <= 120000:
            score += 10
            reasons.append("Good affiliate-value range")
        elif 25000 <= price < 40000:
            score += 8
            reasons.append("Good entry-level affiliate value")
        elif price > 120000:
            score += 7
            reasons.append("High-ticket affiliate opportunity")
        else:
            score += 5

    # -------------------------------------------------
    # Final cap
    # -------------------------------------------------

    score = min(round(score), 100)

    return {
        "score": score,
        "price": price,
        "old_price": old_price,
        "discount_percent": discount,
        "reasons": reasons,
        "metrics": {
            "performance_score": performance_score,
            "market_score": market_score,
            "purchase_intent_score": intent_score,
            "social_marketing_score": social_score,
        },
    }


def is_valid_product(product):
    url = clean_text(product.get("source_url")).lower()
    title = clean_text(product.get("title")).lower()

    for keyword in EXCLUDED_KEYWORDS:
        if keyword in url or keyword in title:
            return False

    if not product.get("product_data"):
        return False

    return True


def run_analysis():
    if not RESEARCH_FILE.exists():
        raise FileNotFoundError(
            f"Research file not found: {RESEARCH_FILE}"
        )

    with open(RESEARCH_FILE, "r", encoding="utf-8") as file:
        research = json.load(file)

    products = research.get("products", [])

    valid_products = []

    for product in products:
        if not is_valid_product(product):
            continue

        product_data = product.get("product_data", {})

        analysis = score_product({
            **product_data,
            "source_url": product.get("source_url"),
        })

        valid_products.append({
            "product_name": clean_text(
                product_data.get("title")
                or product.get("product_name")
            ),
            "source_url": product.get("source_url"),
            "title": clean_text(product_data.get("title")),
            "brand": clean_text(product_data.get("brand")),
            "price": analysis["price"],
            "old_price": analysis["old_price"],
            "discount_percent": analysis["discount_percent"],
            "image": product_data.get("image"),
            "score": analysis["score"],
            "metrics": analysis["metrics"],
            "reasons": analysis["reasons"],
            "research_status": product.get("research_status"),
        })

    valid_products.sort(
        key=lambda product: product["score"],
        reverse=True
    )

    for index, product in enumerate(valid_products, start=1):
        product["rank"] = index

    result = {
        "analysis_status": "completed",
        "source": "Star Tech",
        "total_researched": len(products),
        "valid_products": len(valid_products),
        "products": valid_products,
        "best_product": (
            valid_products[0]
            if valid_products
            else None
        ),
    }

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        json.dump(
            result,
            file,
            ensure_ascii=False,
            indent=2
        )

    return result


if __name__ == "__main__":
    print("Starting product scoring engine...")

    result = run_analysis()

    print()
    print(f"Products researched: {result['total_researched']}")
    print(f"Valid products: {result['valid_products']}")

    print()
    print("TOP 10 PRODUCTS:")

    for product in result["products"][:10]:
        print(
            f"#{product['rank']} | "
            f"Score: {product['score']}/100 | "
            f"{product['title']}"
        )

    print()
    if result["best_product"]:
        best = result["best_product"]

        print("BEST PRODUCT SELECTED:")
        print(f"Title: {best['title']}")
        print(f"Price: {best['price']}")
        print(f"Discount: {best['discount_percent']}%")
        print(f"Score: {best['score']}/100")
        print(f"URL: {best['source_url']}")

    print()
    print("Product scoring completed.")
    print(f"Saved to: {OUTPUT_FILE}")

