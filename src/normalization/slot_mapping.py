"""Category-to-slot mapping used across all approaches."""

SLOTS = ("top", "bottom", "dress", "outerwear", "shoes", "accessory", "bag")

CATEGORY_TO_SLOT = {
    "tops": "top",
    "t-shirts": "top",
    "shirts": "top",
    "blouses": "top",
    "sweaters": "top",
    "bottoms": "bottom",
    "pants": "bottom",
    "jeans": "bottom",
    "skirts": "bottom",
    "shorts": "bottom",
    "dresses": "dress",
    "outerwear": "outerwear",
    "jackets": "outerwear",
    "coats": "outerwear",
    "shoes": "shoes",
    "sneakers": "shoes",
    "boots": "shoes",
    "heels": "shoes",
    "bags": "bag",
    "handbags": "bag",
    "jewellery": "accessory",
    "jewelry": "accessory",
    "accessories": "accessory",
    "hats": "accessory",
    "scarves": "accessory",
}


def map_category_to_slot(raw_category: str | None) -> str | None:
    if not raw_category:
        return None
    key = raw_category.strip().lower()
    if key in CATEGORY_TO_SLOT:
        return CATEGORY_TO_SLOT[key]
    for cat, slot in CATEGORY_TO_SLOT.items():
        if cat in key:
            return slot
    return None
