import json
import re
import requests
from pathlib import Path
from bs4 import BeautifulSoup


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/154.0.0.0 Safari/537.36"
    )
}


def fetch_page(url):
    response = requests.get(
        url,
        timeout=20,
        headers=HEADERS
    )

    response.raise_for_status()

    return {
        "status_code": response.status_code,
        "url": response.url,
        "content_length": len(response.text),
        "html": response.text
    }


def clean_text(text):
    if not text:
        return None

    return re.sub(r"\s+", " ", text).strip()


def extract_title(soup):
    selectors = [
        'meta[property="og:title"]',
        "h1",
        "title"
    ]

    for selector in selectors:
        element = soup.select_one(selector)

        if element:
            value = (
                element.get("content")
                or element.get_text(
                    " ",
                    strip=True
                )
            )

            value = clean_text(value)

            if value:
                return value

    return None


def extract_description(soup):
    selectors = [
        'meta[name="description"]',
        'meta[property="og:description"]',
        '[itemprop="description"]'
    ]

    for selector in selectors:
        element = soup.select_one(selector)

        if element:
            value = (
                element.get("content")
                or element.get_text(
                    " ",
                    strip=True
                )
            )

            value = clean_text(value)

            if value:
                return value

    return None


def extract_price(soup):
    selectors = [
        '[itemprop="price"]',
        ".price",
        ".product-price",
        ".sale-price",
        ".current-price",
        ".price-new"
    ]

    for selector in selectors:
        element = soup.select_one(selector)

        if element:
            value = (
                element.get("content")
                or element.get_text(
                    " ",
                    strip=True
                )
            )

            value = clean_text(value)

            if value:
                return value

    return None


def extract_old_price(soup):
    selectors = [
        ".old-price",
        ".old-price-value",
        ".regular-price",
        ".list-price",
        ".was-price",
        ".previous-price",
        ".price-old",
        "[data-old-price]"
    ]

    for selector in selectors:
        element = soup.select_one(selector)

        if element:
            value = (
                element.get("content")
                or element.get("data-old-price")
                or element.get_text(
                    " ",
                    strip=True
                )
            )

            value = clean_text(value)

            if value:
                return value

    return None


def extract_discount(soup):
    selectors = [
        ".discount",
        ".discount-percent",
        ".discount-percentage",
        ".save-percent",
        ".discount-tag",
        "[data-discount]"
    ]

    for selector in selectors:
        element = soup.select_one(selector)

        if element:
            value = (
                element.get("data-discount")
                or element.get_text(
                    " ",
                    strip=True
                )
            )

            value = clean_text(value)

            if value:
                return value

    return None


def extract_brand(soup):
    selectors = [
        '[itemprop="brand"]',
        ".brand",
        ".product-brand",
        ".brand-name"
    ]

    for selector in selectors:
        element = soup.select_one(selector)

        if element:
            value = (
                element.get("content")
                or element.get_text(
                    " ",
                    strip=True
                )
            )

            value = clean_text(value)

            if value:
                return value

    return None


def extract_category(soup):
    selectors = [
        '[itemprop="category"]',
        ".breadcrumb",
        ".breadcrumbs",
        ".product-category",
        ".category"
    ]

    for selector in selectors:
        element = soup.select_one(selector)

        if element:
            value = clean_text(
                element.get_text(
                    " ",
                    strip=True
                )
            )

            if value:
                return value

    return None


def extract_availability(soup):
    selectors = [
        '[itemprop="availability"]',
        ".availability",
        ".stock",
        ".stock-status",
        ".availability-status",
        ".product-stock"
    ]

    for selector in selectors:
        element = soup.select_one(selector)

        if element:
            value = (
                element.get("content")
                or element.get_text(
                    " ",
                    strip=True
                )
            )

            value = clean_text(value)

            if value:
                return value

    return None


def extract_image(soup):
    selectors = [
        'meta[property="og:image"]',
        '[itemprop="image"]',
        ".product-image img",
        ".product-gallery img",
        ".product img"
    ]

    for selector in selectors:
        element = soup.select_one(selector)

        if element:
            value = (
                element.get("content")
                or element.get("src")
                or element.get("data-src")
            )

            if value:
                return value.strip()

    return None


def extract_specifications(soup):
    specifications = {}

    for table in soup.find_all("table"):

        for row in table.find_all("tr"):

            cells = row.find_all(
                ["th", "td"]
            )

            if len(cells) >= 2:

                key = clean_text(
                    cells[0].get_text(
                        " ",
                        strip=True
                    )
                )

                value = clean_text(
                    cells[1].get_text(
                        " ",
                        strip=True
                    )
                )

                if key and value:
                    specifications[key] = value

    return specifications


def extract_basic_product_data(html):

    soup = BeautifulSoup(
        html,
        "html.parser"
    )

    return {
        "title": extract_title(soup),
        "description": extract_description(soup),
        "price": extract_price(soup),
        "old_price": extract_old_price(soup),
        "discount": extract_discount(soup),
        "availability": extract_availability(soup),
        "brand": extract_brand(soup),
        "category": extract_category(soup),
        "image": extract_image(soup),
        "specifications": extract_specifications(soup)
    }


def product_research(
    product_name,
    source_url
):

    result = {
        "product_name": product_name,
        "source_url": source_url,
        "research_status": "pending",
        "source_data": None,
        "product_data": None
    }

    try:

        page = fetch_page(
            source_url
        )

        result["source_data"] = {
            "status_code": page["status_code"],
            "url": page["url"],
            "content_length": page["content_length"]
        }

        result["product_data"] = (
            extract_basic_product_data(
                page["html"]
            )
        )

        result["research_status"] = (
            "completed"
        )

    except Exception as error:

        result["research_status"] = "failed"
        result["error"] = str(error)

    return result


def load_discovery():

    discovery_file = (
        Path(__file__).resolve().parent.parent
        / "data"
        / "discovery"
        / "latest.json"
    )

    if not discovery_file.exists():
        raise FileNotFoundError(
            "Discovery latest.json was not found."
        )

    with open(
        discovery_file,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


def batch_product_research():

    discovery = load_discovery()

    urls = discovery.get(
        "product_urls",
        []
    )

    products = []

    total = len(urls)

    print(
        f"Found {total} discovered products."
    )

    for number, url in enumerate(
        urls,
        start=1
    ):

        print()
        print(
            f"[{number}/{total}] Researching..."
        )
        print(url)

        result = product_research(
            product_name=f"Product {number}",
            source_url=url
        )

        products.append(result)

        print(
            "Status:",
            result["research_status"]
        )

    return {
        "research_status": "completed",
        "source": "Star Tech",
        "category_url": discovery.get(
            "category_url"
        ),
        "discovered_product_count": total,
        "researched_product_count": len(
            products
        ),
        "products": products
    }


def save_research(data):

    output_dir = (
        Path(__file__).resolve().parent.parent
        / "data"
        / "research"
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


if __name__ == "__main__":

    print(
        "Starting automated product research..."
    )

    result = batch_product_research()

    output_file = save_research(
        result
    )

    print()
    print(
        "Product research completed."
    )

    print(
        "Products discovered:",
        result[
            "discovered_product_count"
        ]
    )

    print(
        "Products researched:",
        result[
            "researched_product_count"
        ]
    )

    print(
        "Saved to:",
        output_file
    )
