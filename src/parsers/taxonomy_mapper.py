"""Source-taxonomy-first parser (Approach 3).

Maps a client's source category directly to the internal slot, preserves the
raw source category, and tracks confidence / provenance. Qwen is only used
downstream if required fields are still missing.
"""
from __future__ import annotations

from typing import Dict

from src.common import MetadataParser, NormalizedItem
from src.normalization.slot_mapping import map_category_to_slot
from src.utils.provenance import mark, SOURCE_METADATA, TEXT_INFERENCE


SOURCE_TO_SLOT: Dict[str, str] = {
    "tops": "top",
    "bottoms": "bottom",
    "outerwear": "outerwear",
    "shoes": "shoes",
    "bags": "bag",
    "jewellery": "accessory",
    "jewelry": "accessory",
    "accessories": "accessory",
    "dresses": "dress",
}


class TaxonomyMapper(MetadataParser):
    def __init__(self, overrides: Dict[str, str] | None = None):
        self.mapping = {**SOURCE_TO_SLOT, **(overrides or {})}

    def parse(self, item: NormalizedItem) -> NormalizedItem:
        if not item.raw_category:
            return item
        key = item.raw_category.strip().lower()
        if key in self.mapping:
            if not item.slot:
                item.slot = self.mapping[key]
                mark(item, "slot", SOURCE_METADATA)
            return item
        inferred = map_category_to_slot(item.raw_category)
        if inferred and not item.slot:
            item.slot = inferred
            mark(item, "slot", TEXT_INFERENCE)
        return item
