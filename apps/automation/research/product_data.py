PRODUCT_TEXT_FIELDS = (
    "title",
    "description",
    "price",
    "old_price",
    "discount",
    "availability",
    "brand",
    "category",
    "image",
)


def is_usable_product_data(product_data):
    if not isinstance(product_data, dict):
        return False

    specifications = product_data.get("specifications", {})
    if not isinstance(specifications, dict):
        return False

    if any(
        isinstance(product_data.get(field), str)
        and product_data[field].strip()
        for field in PRODUCT_TEXT_FIELDS
    ):
        return True

    return any(
        isinstance(key, str)
        and key.strip()
        and isinstance(value, str)
        and value.strip()
        for key, value in specifications.items()
    )
