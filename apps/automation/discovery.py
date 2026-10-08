import json
import re
import requests
from pathlib import Path
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup


# ==================================================
# STAR TECH CATEGORY
# ==================================================

STARTECH_CATEGORY_URL = (
    "https://www.startech.com.bd/"
    "laptop-notebook/laptop"
)


# ==================================================
# REQUEST HEADERS
# ==================================================

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/154.0.0.0 Safari/537.36"
    )
}


# ==================================================
# FETCH CATEGORY PAGE
# ==================================================

def fetch_category_page(url):

    response = requests.get(
        url,
        timeout=20,
        headers=HEADERS
    )

    response.raise_for_status()

    return response.text


# ==================================================
# NORMALIZE URL
# ==================================================

def normalize_url(url):

    url = url.split("#")[0]
    url = url.split("?")[0]

    return url.rstrip("/")


# ==================================================
# CHECK STAR TECH URL
# ==================================================

def is_startech_url(url):

    parsed = urlparse(url)

    return parsed.netloc in {
        "www.startech.com.bd",
        "startech.com.bd"
    }


# ==================================================
# PRODUCT TITLE CHECK
# ==================================================

def looks_like_product_title(title):

    if not title:
        return False

    title = " ".join(title.split())

    if len(title) < 20:
        return False

    blocked_titles = {
        "laptop",
        "lenovo",
        "msi",
        "hp",
        "asus",
        "tecno",
        "macbook",
        "gaming laptop",
        "gigabyte",
        "acer",
        "dell",
        "smart laptop",
        "chuwi",
        "microsoft",
        "walton",
        "compare",
        "buy now",
        "add to compare"
    }

    if title.lower() in blocked_titles:
        return False

    return True


# ==================================================
# PRICE CHECK
# ==================================================

def has_price(text):

    if not text:
        return False

    if "৳" in text:
        return True

    if re.search(
        r"\b\d[\d,]*\s*(bdt|tk)\b",
        text,
        re.IGNORECASE
    ):
        return True

    return False


# ==================================================
# BUY NOW CHECK
# ==================================================

def has_buy_now(text):

    if not text:
        return False

    return "buy now" in text.lower()


# ==================================================
# BLOCKED PATH CHECK
# ==================================================

def is_blocked_path(url):

    path = urlparse(url).path.lower().strip("/")

    blocked_paths = [

        # General information
        "information",
        "information/offer",

        # Promotions / tools
        "happy-hour",
        "tool",
        "tool/pc_builder",

        # Blog / news
        "blog",
        "news",

        # Category / brand pages
        "category",
        "brand",

        # Non-product policy pages
        "warranty-policy",
        "refund-policy",

        # Other known non-product pages
        "privacy-policy",
        "terms-and-conditions",
        "contact-us",
        "about-us"
    ]

    for blocked in blocked_paths:

        if path == blocked:
            return True

        if path.startswith(blocked + "/"):
            return True

    return False


# ==================================================
# EXTRACT PRODUCT URLS
# ==================================================

def extract_product_urls(html, base_url):

    soup = BeautifulSoup(
        html,
        "html.parser"
    )

    product_urls = []

    seen = set()

    for link in soup.find_all(
        "a",
        href=True
    ):

        href = link.get("href")

        if not href:
            continue

        # Build absolute URL
        full_url = normalize_url(
            urljoin(
                base_url,
                href
            )
        )

        # Only Star Tech URLs
        if not is_startech_url(full_url):
            continue

        # Avoid duplicates
        if full_url in seen:
            continue

        # Skip known non-product paths
        if is_blocked_path(full_url):
            continue

        # Extract visible link title
        title = link.get_text(
            " ",
            strip=True
        )

        # Check whether title looks like a product
        if not looks_like_product_title(title):
            continue

        # Look upward through parent containers
        current = link

        for _ in range(8):

            if current is None:
                break

            container_text = current.get_text(
                " ",
                strip=True
            )

            # Product cards normally contain both
            # price and Buy Now
            if (
                has_price(container_text)
                and has_buy_now(container_text)
            ):

                seen.add(full_url)

                product_urls.append(
                    full_url
                )

                break

            current = current.parent

    return product_urls


# ==================================================
# DISCOVER PRODUCTS
# ==================================================

def discover_products(
    category_url=STARTECH_CATEGORY_URL
):

    try:

        html = fetch_category_page(
            category_url
        )

        product_urls = extract_product_urls(
            html,
            category_url
        )

        return {
            "discovery_status": "completed",
            "source": "Star Tech",
            "category_url": category_url,
            "product_count": len(product_urls),
            "product_urls": product_urls
        }

    except requests.RequestException as error:

        return {
            "discovery_status": "failed",
            "source": "Star Tech",
            "category_url": category_url,
            "product_count": 0,
            "product_urls": [],
            "error": str(error)
        }


# ==================================================
# SAVE DISCOVERY RESULT
# ==================================================

def save_discovery(data):

    output_dir = (
        Path(__file__).resolve().parent
        / "data"
        / "discovery"
    )

    output_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    output_file = (
        output_dir
        / "latest.json"
    )

    with open(
        output_file,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            data,
            file,
            indent=2,
            ensure_ascii=False
        )

    return output_file


# ==================================================
# MAIN
# ==================================================

if __name__ == "__main__":

    result = discover_products()

    file_path = save_discovery(
        result
    )

    print(
        "Product discovery completed."
    )

    print(
        "Products found:",
        result["product_count"]
    )

    print(
        "Saved to:",
        file_path
    )

    if result["product_urls"]:

        print(
            "\nFirst discovered products:"
        )

        for url in result[
            "product_urls"
        ][:10]:

            print(url)

    else:

        print(
            "\nNo product URLs were discovered."
        )