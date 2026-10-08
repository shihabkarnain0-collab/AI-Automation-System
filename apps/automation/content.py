import json
import re
from pathlib import Path


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

OUTPUT_DIR = (
    PROJECT_DIR
    / "apps"
    / "automation"
    / "data"
    / "content"
)

OUTPUT_FILE = OUTPUT_DIR / "latest.json"


# ==================================================
# CLEAN BRAND NAME
# ==================================================

def clean_brand(brand):

    if not brand:
        return "N/A"

    brand = str(brand).strip()

    if brand.lower().startswith("brand "):
        brand = brand[6:].strip()

    return brand


# ==================================================
# FIND AFFILIATE URL
# ==================================================

def find_affiliate_url(
    affiliate_data,
    product_name,
    source_url
):

    products = affiliate_data.get(
        "products",
        []
    )

    # Exact URL match
    for product in products:

        if product.get("source_url") == source_url:

            affiliate_url = product.get(
                "affiliate_url"
            )

            if affiliate_url:
                return affiliate_url

    # Exact product name match
    for product in products:

        if product.get("product_name") == product_name:

            affiliate_url = product.get(
                "affiliate_url"
            )

            if affiliate_url:
                return affiliate_url

    return None


# ==================================================
# FORMAT PRICE
# ==================================================

def format_price(price):

    if isinstance(price, (int, float)):

        return f"৳{price:,.0f}"

    return "Price unavailable"


# ==================================================
# FORMAT OLD PRICE
# ==================================================

def format_old_price(old_price):

    if isinstance(old_price, (int, float)):

        return f"৳{old_price:,.0f}"

    return "N/A"


# ==================================================
# CALCULATE DISCOUNT
# ==================================================

def calculate_discount(price, old_price):

    if (
        isinstance(price, (int, float))
        and isinstance(old_price, (int, float))
        and old_price > 0
        and old_price > price
    ):

        discount = (
            (old_price - price)
            / old_price
        ) * 100

        return round(discount, 2)

    return 0


# ==================================================
# CLEAN TEXT
# ==================================================

def clean_text(value):

    if value is None:
        return ""

    return " ".join(
        str(value).split()
    )


# ==================================================
# SPECIFICATION TEXT
# ==================================================

def specifications_to_text(specifications):

    if not specifications:
        return ""

    if isinstance(
        specifications,
        dict
    ):

        parts = []

        for key, value in specifications.items():

            key_text = clean_text(key)
            value_text = clean_text(value)

            if key_text and value_text:

                parts.append(
                    f"{key_text}: {value_text}"
                )

        return " | ".join(parts)

    if isinstance(
        specifications,
        list
    ):

        return " | ".join(
            clean_text(item)
            for item in specifications
            if clean_text(item)
        )

    return clean_text(
        specifications
    )


# ==================================================
# DETECT PRODUCT FEATURES
# ==================================================

def detect_features(best_product):

    features = []

    product_name = clean_text(
        best_product.get(
            "product_name",
            ""
        )
    )

    specifications = specifications_to_text(
        best_product.get(
            "specifications"
        )
    )

    combined_text = (
        product_name
        + " "
        + specifications
    ).lower()

    # RAM
    ram_match = re.search(
        r"(\d+)\s*gb\s*(?:ram|memory)?",
        combined_text
    )

    if ram_match:

        ram = ram_match.group(1)

        features.append(
            f"{ram}GB RAM"
        )

    # Storage
    storage_match = re.search(
        r"(\d+)\s*(gb|tb)\s*(?:ssd|nvme|storage)",
        combined_text
    )

    if storage_match:

        storage = storage_match.group(1)
        unit = storage_match.group(2).upper()

        features.append(
            f"{storage}{unit} storage"
        )

    # Ryzen
    if "ryzen" in combined_text:

        features.append(
            "AMD Ryzen processor"
        )

    # Intel Core
    if "core i3" in combined_text:

        features.append(
            "Intel Core i3 processor"
        )

    elif "core i5" in combined_text:

        features.append(
            "Intel Core i5 processor"
        )

    elif "core i7" in combined_text:

        features.append(
            "Intel Core i7 processor"
        )

    # RTX
    rtx_match = re.search(
        r"rtx\s*(\d+)",
        combined_text
    )

    if rtx_match:

        features.append(
            f"RTX {rtx_match.group(1)} graphics"
        )

    # Display
    if (
        "fhd" in combined_text
        or "full hd" in combined_text
    ):

        features.append(
            "Full HD display"
        )

    # Gaming
    if "gaming" in combined_text:

        features.append(
            "gaming-focused hardware"
        )

    # Remove duplicates
    unique_features = []

    for feature in features:

        if feature not in unique_features:

            unique_features.append(
                feature
            )

    return unique_features[:5]


# ==================================================
# GENERATE SELLING POINTS
# ==================================================

def generate_selling_points(
    best_product,
    score,
    discount
):

    features = detect_features(
        best_product
    )

    selling_points = []

    if features:

        for feature in features:

            selling_points.append(
                feature
            )

    if score >= 80:

        selling_points.append(
            "strong overall value based on our product scoring system"
        )

    elif score >= 70:

        selling_points.append(
            "good overall value based on our product scoring system"
        )

    if discount >= 5:

        selling_points.append(
            f"{discount}% price advantage"
        )

    return selling_points[:6]


# ==================================================
# GENERATE MARKETING ANGLE
# ==================================================

def generate_marketing_angle(
    best_product,
    score,
    discount
):

    product_name = clean_text(
        best_product.get(
            "product_name",
            ""
        )
    ).lower()

    if "gaming" in product_name:

        return (
            "Gaming and performance-focused users "
            "may find this configuration worth considering."
        )

    if score >= 80 and discount >= 5:

        return (
            "A strong combination of performance, "
            "price and overall value."
        )

    if score >= 80:

        return (
            "A strong overall choice based on "
            "our automated product evaluation."
        )

    if discount >= 5:

        return (
            "An attractive option for buyers "
            "looking for better value."
        )

    return (
        "A product worth considering based on "
        "our automated evaluation."
    )


# ==================================================
# GENERATE HASHTAGS
# ==================================================

def generate_hashtags(
    best_product,
    brand
):

    product_name = clean_text(
        best_product.get(
            "product_name",
            ""
        )
    ).lower()

    hashtags = [
        "#Laptop",
        "#LaptopBangladesh",
        "#TechDeals",
        "#StarTech",
        "#NOCTÉRA"
    ]

    if brand and brand != "N/A":

        clean_brand_tag = re.sub(
            r"[^a-zA-Z0-9]",
            "",
            brand
        )

        if clean_brand_tag:

            hashtags.insert(
                1,
                f"#{clean_brand_tag}"
            )

    if "gaming" in product_name:

        hashtags.append(
            "#GamingLaptop"
        )

    elif "macbook" in product_name:

        hashtags.append(
            "#MacBook"
        )

    return " ".join(
        dict.fromkeys(hashtags)
    )


# ==================================================
# GENERATE FACEBOOK POST
# ==================================================

def generate_facebook_post(
    best_product,
    affiliate_url
):

    product_name = clean_text(
        best_product.get(
            "product_name",
            "Product"
        )
    )

    brand = clean_brand(
        best_product.get(
            "brand"
        )
    )

    price = best_product.get(
        "price"
    )

    old_price = best_product.get(
        "old_price"
    )

    score = best_product.get(
        "score",
        0
    )

    discount = calculate_discount(
        price,
        old_price
    )

    price_text = format_price(
        price
    )

    old_price_text = format_old_price(
        old_price
    )

    selling_points = generate_selling_points(
        best_product,
        score,
        discount
    )

    marketing_angle = generate_marketing_angle(
        best_product,
        score,
        discount
    )

    hashtags = generate_hashtags(
        best_product,
        brand
    )

    # --------------------------------------------------
    # Selling point section
    # --------------------------------------------------

    if selling_points:

        feature_text = "\n".join(
            f"• {point}"
            for point in selling_points
        )

    else:

        feature_text = (
            "• Evaluated for price, performance "
            "and overall value"
        )

    # --------------------------------------------------
    # Facebook post
    # --------------------------------------------------

    post = f"""🔥 {product_name}

💻 Brand: {brand}

💰 Current Price: {price_text}
🏷️ Regular Price: {old_price_text}

⭐ AI Product Score: {score}/100

Why consider it?

{feature_text}

💡 Our take:
{marketing_angle}

🔗 বিস্তারিত ও কেনার জন্য:
{affiliate_url}

⚠️ Disclaimer: এই পোস্টের affiliate link ব্যবহার করে NOCTÉRA কমিশন পেতে পারে। আপনার অতিরিক্ত কোনো খরচ হবে না।

{hashtags}
"""

    return post, selling_points, marketing_angle


# ==================================================
# MAIN
# ==================================================

def main():

    print(
        "Starting enhanced content generation..."
    )

    print()

    # --------------------------------------------------
    # Check analysis
    # --------------------------------------------------

    if not ANALYSIS_FILE.exists():

        print(
            "ERROR: Analysis file not found."
        )

        return

    # --------------------------------------------------
    # Check affiliate
    # --------------------------------------------------

    if not AFFILIATE_FILE.exists():

        print(
            "ERROR: Affiliate file not found."
        )

        print(
            "Run affiliate.py first."
        )

        return

    # --------------------------------------------------
    # Read analysis
    # --------------------------------------------------

    try:

        with open(
            ANALYSIS_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            analysis_data = json.load(
                file
            )

    except (
        OSError,
        json.JSONDecodeError
    ) as error:

        print(
            "ERROR: Could not read analysis data."
        )

        print(error)

        return

    # --------------------------------------------------
    # Read affiliate data
    # --------------------------------------------------

    try:

        with open(
            AFFILIATE_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            affiliate_data = json.load(
                file
            )

    except (
        OSError,
        json.JSONDecodeError
    ) as error:

        print(
            "ERROR: Could not read affiliate data."
        )

        print(error)

        return

    # --------------------------------------------------
    # Best product
    # --------------------------------------------------

    best_product = analysis_data.get(
        "best_product"
    )

    if not best_product:

        print(
            "ERROR: best_product not found."
        )

        return

    # --------------------------------------------------
    # Product identity
    # --------------------------------------------------

    product_name = best_product.get(
        "product_name",
        "Product"
    )

    source_url = best_product.get(
        "source_url"
    )

    score = best_product.get(
        "score",
        0
    )

    # --------------------------------------------------
    # Affiliate URL
    # --------------------------------------------------

    affiliate_url = find_affiliate_url(
        affiliate_data,
        product_name,
        source_url
    )

    if not affiliate_url:

        print(
            "ERROR: Matching affiliate_url not found."
        )

        print(
            f"Product: {product_name}"
        )

        return

    # --------------------------------------------------
    # Generate enhanced content
    # --------------------------------------------------

    post, selling_points, marketing_angle = (
        generate_facebook_post(
            best_product,
            affiliate_url
        )
    )

    # --------------------------------------------------
    # Clean brand
    # --------------------------------------------------

    brand = clean_brand(
        best_product.get(
            "brand"
        )
    )

    # --------------------------------------------------
    # Price
    # --------------------------------------------------

    price = best_product.get(
        "price"
    )

    old_price = best_product.get(
        "old_price"
    )

    discount = calculate_discount(
        price,
        old_price
    )

    # --------------------------------------------------
    # Output
    # --------------------------------------------------

    output_data = {

        "content_status": "completed",

        "content_type": "enhanced_facebook_post",

        "product_name": product_name,

        "brand": brand,

        "price": price,

        "old_price": old_price,

        "discount": discount,

        "score": score,

        "source_url": source_url,

        "affiliate_url": affiliate_url,

        "selling_points": selling_points,

        "marketing_angle": marketing_angle,

        "post": post
    }

    # --------------------------------------------------
    # Save
    # --------------------------------------------------

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

    # --------------------------------------------------
    # Success
    # --------------------------------------------------

    print(
        "Enhanced content generated successfully!"
    )

    print()

    print(post)

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

    main()