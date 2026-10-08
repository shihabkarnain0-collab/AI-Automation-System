import json
import os
from pathlib import Path
from urllib.parse import urlparse, parse_qsl, urlencode, urlunparse

from dotenv import load_dotenv


# --------------------------------------------------
# PATH SETUP
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[2]

ANALYSIS_FILE = BASE_DIR / "apps" / "automation" / "data" / "analysis" / "latest.json"
OUTPUT_DIR = BASE_DIR / "apps" / "automation" / "data" / "affiliate"
OUTPUT_FILE = OUTPUT_DIR / "latest.json"

ENV_FILE = BASE_DIR / ".env"


# --------------------------------------------------
# LOAD ENVIRONMENT
# --------------------------------------------------

load_dotenv(ENV_FILE)

AFFILIATE_CODE = os.getenv("STARTECH_AFFILIATE_CODE")


# --------------------------------------------------
# AFFILIATE URL BUILDER
# --------------------------------------------------

def build_affiliate_url(product_url):
    """
    Add the Star Tech affiliate tracking code
    to a product URL safely.
    """

    if not product_url:
        return None

    if not AFFILIATE_CODE:
        raise ValueError(
            "STARTECH_AFFILIATE_CODE is missing from .env"
        )

    parsed = urlparse(product_url)

    query_params = dict(parse_qsl(parsed.query))

    # Change this parameter if Star Tech's
    # affiliate system uses a different parameter.
    query_params["ref"] = AFFILIATE_CODE

    new_query = urlencode(query_params)

    affiliate_url = urlunparse(
        (
            parsed.scheme,
            parsed.netloc,
            parsed.path,
            parsed.params,
            new_query,
            parsed.fragment,
        )
    )

    return affiliate_url


# --------------------------------------------------
# LOAD ANALYSIS DATA
# --------------------------------------------------

def load_analysis_data():
    if not ANALYSIS_FILE.exists():
        raise FileNotFoundError(
            f"Analysis file not found: {ANALYSIS_FILE}"
        )

    with open(ANALYSIS_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


# --------------------------------------------------
# GENERATE AFFILIATE DATA
# --------------------------------------------------

def generate_affiliate_data(data):
    products = data.get("products", [])

    affiliate_products = []

    for index, product in enumerate(products, start=1):

        source_url = product.get("source_url")

        try:
            affiliate_url = build_affiliate_url(source_url)

        except Exception as error:
            affiliate_url = None
            print(
                f"Warning: Could not create affiliate URL "
                f"for product #{index}: {error}"
            )

        affiliate_products.append(
            {
                "rank": product.get("rank", index),
                "product_name": product.get("product_name"),
                "source_url": source_url,
                "affiliate_url": affiliate_url,
                "price": product.get("price"),
                "discount": product.get("discount"),
                "availability": product.get("availability"),
                "brand": product.get("brand"),
                "score": product.get("score"),
                "image": product.get("image"),
            }
        )

    return affiliate_products


# --------------------------------------------------
# SAVE OUTPUT
# --------------------------------------------------

def save_output(products):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    output_data = {
        "affiliate_status": "completed",
        "source": "Star Tech",
        "affiliate_code_configured": bool(AFFILIATE_CODE),
        "product_count": len(products),
        "products": products,
    }

    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        json.dump(
            output_data,
            file,
            ensure_ascii=False,
            indent=2,
        )

    return output_data


# --------------------------------------------------
# MAIN
# --------------------------------------------------

def main():

    print("=== Star Tech Affiliate Generator ===")
    print()

    if not AFFILIATE_CODE:
        print("ERROR: STARTECH_AFFILIATE_CODE is not configured.")
        print("Please add it to the .env file.")
        return

    data = load_analysis_data()

    products = generate_affiliate_data(data)

    output_data = save_output(products)

    print(f"Products processed: {len(products)}")
    print(f"Affiliate file saved: {OUTPUT_FILE}")
    print()
    print("Affiliate generation completed.")


if __name__ == "__main__":
    main()