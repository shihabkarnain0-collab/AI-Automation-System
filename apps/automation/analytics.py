import json
from pathlib import Path
from datetime import datetime


# ==================================================
# PATHS
# ==================================================

BASE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BASE_DIR.parent.parent

ANALYSIS_FILE = (
    PROJECT_DIR
    / "apps"
    / "automation"
    / "data"
    / "analysis"
    / "latest.json"
)

AFFILIATE_FILE = (
    PROJECT_DIR
    / "apps"
    / "automation"
    / "data"
    / "affiliate"
    / "latest.json"
)

CONTENT_FILE = (
    PROJECT_DIR
    / "apps"
    / "automation"
    / "data"
    / "content"
    / "latest.json"
)

OUTPUT_DIR = (
    PROJECT_DIR
    / "apps"
    / "automation"
    / "data"
    / "analytics"
)

OUTPUT_FILE = OUTPUT_DIR / "latest.json"


# ==================================================
# LOAD JSON
# ==================================================

def load_json(file_path):

    if not file_path.exists():
        raise FileNotFoundError(
            f"File not found: {file_path}"
        )

    with open(
        file_path,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


# ==================================================
# SAFE NUMBER
# ==================================================

def safe_number(value, default=0):

    if isinstance(value, (int, float)):
        return value

    try:
        return float(value)

    except (TypeError, ValueError):
        return default


# ==================================================
# ANALYZE PRODUCT
# ==================================================

def analyze_product(
    analysis_data,
    affiliate_data,
    content_data
):

    best_product = analysis_data.get(
        "best_product"
    )

    if not best_product:

        raise ValueError(
            "best_product not found in analysis data."
        )

    product_name = best_product.get(
        "product_name",
        "Unknown Product"
    )

    score = safe_number(
        best_product.get("score")
    )

    price = safe_number(
        best_product.get("price")
    )

    old_price = safe_number(
        best_product.get("old_price")
    )

    # ----------------------------------------------
    # Affiliate matching
    # ----------------------------------------------

    affiliate_url = None

    for product in affiliate_data.get(
        "products",
        []
    ):

        if (
            product.get("product_name")
            == product_name
        ):

            affiliate_url = product.get(
                "affiliate_url"
            )

            break

    # ----------------------------------------------
    # Content status
    # ----------------------------------------------

    content_status = content_data.get(
        "content_status",
        "unknown"
    )

    content_type = content_data.get(
        "content_type",
        "unknown"
    )

    post_generated = bool(
        content_data.get("post")
    )

    # ----------------------------------------------
    # Discount
    # ----------------------------------------------

    discount = 0

    if old_price > price and old_price > 0:

        discount = round(
            (
                (old_price - price)
                / old_price
            ) * 100,
            2
        )

    # ----------------------------------------------
    # Readiness
    # ----------------------------------------------

    ready_for_marketing = bool(
        affiliate_url
        and post_generated
        and score > 0
    )

    return {
        "product_name": product_name,
        "score": score,
        "price": price,
        "old_price": old_price,
        "discount": discount,
        "affiliate_url_found": bool(
            affiliate_url
        ),
        "content_generated": post_generated,
        "content_status": content_status,
        "content_type": content_type,
        "ready_for_marketing": ready_for_marketing
    }


# ==================================================
# GENERATE ANALYTICS
# ==================================================

def generate_analytics():

    print(
        "Starting analytics engine..."
    )

    print()

    # ----------------------------------------------
    # Load files
    # ----------------------------------------------

    analysis_data = load_json(
        ANALYSIS_FILE
    )

    affiliate_data = load_json(
        AFFILIATE_FILE
    )

    content_data = load_json(
        CONTENT_FILE
    )

    # ----------------------------------------------
    # Analyze
    # ----------------------------------------------

    product_report = analyze_product(
        analysis_data,
        affiliate_data,
        content_data
    )

    # ----------------------------------------------
    # Summary
    # ----------------------------------------------

    affiliate_products = affiliate_data.get(
        "products",
        []
    )

    total_affiliate_products = len(
        affiliate_products
    )

    total_analyzed_products = len(
        analysis_data.get(
            "products",
            []
        )
    )

    output_data = {

        "analytics_status": "completed",

        "generated_at": datetime.now().isoformat(
            timespec="seconds"
        ),

        "pipeline": {
            "analysis": True,
            "affiliate": True,
            "content": True,
            "analytics": True
        },

        "summary": {
            "products_analyzed":
                total_analyzed_products,

            "affiliate_products":
                total_affiliate_products,

            "best_product":
                product_report["product_name"],

            "best_product_score":
                product_report["score"],

            "ready_for_marketing":
                product_report[
                    "ready_for_marketing"
                ]
        },

        "best_product_report":
            product_report
    }

    # ----------------------------------------------
    # Save
    # ----------------------------------------------

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            output_data,
            file,
            ensure_ascii=False,
            indent=2
        )

    # ----------------------------------------------
    # Console
    # ----------------------------------------------

    print(
        "Analytics completed successfully!"
    )

    print()

    print(
        f"Products analyzed: "
        f"{total_analyzed_products}"
    )

    print(
        f"Affiliate products: "
        f"{total_affiliate_products}"
    )

    print(
        f"Best product: "
        f"{product_report['product_name']}"
    )

    print(
        f"Score: "
        f"{product_report['score']}/100"
    )

    print(
        f"Ready for marketing: "
        f"{product_report['ready_for_marketing']}"
    )

    print()

    print(
        "Saved to:"
    )

    print(
        OUTPUT_FILE
    )


# ==================================================
# RUN
# ==================================================

if __name__ == "__main__":

    try:

        generate_analytics()

    except Exception as error:

        print(
            "ERROR: Analytics engine failed."
        )

        print(
            error
        )