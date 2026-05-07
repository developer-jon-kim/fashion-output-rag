"""Normalize Polyvore item records into `NormalizedItem` instances."""
from __future__ import annotations

from typing import Dict, Any, Iterable, List

from src.common import NormalizedItem
from .slot_mapping import map_category_to_slot


def _clean(s: Any) -> str | None:
    if s is None:
        return None
    s = str(s).strip()
    return s or None


def normalize_polyvore_item(raw: Dict[str, Any]) -> NormalizedItem:
    raw_category = _clean(raw.get("category") or raw.get("semantic_category"))
    slot = map_category_to_slot(raw_category)

    metadata_source: Dict[str, str] = {}
    if raw.get("category"):
        metadata_source["raw_category"] = "source"
    if slot:
        metadata_source["slot"] = "source" if raw_category else "inferred"
    if raw.get("title"):
        metadata_source["title"] = "source"

    return NormalizedItem(
        item_id=str(raw.get("item_id") or raw.get("id")),
        image_path_or_url=str(raw.get("image") or raw.get("image_path") or ""),
        title=_clean(raw.get("title") or raw.get("name")),
        description=_clean(raw.get("description")),
        raw_category=raw_category,
        slot=slot,
        subcategory=_clean(raw.get("subcategory")),
        department=_clean(raw.get("department")),
        colors=list(raw.get("colors") or []),
        material=_clean(raw.get("material")),
        pattern=_clean(raw.get("pattern")),
        season=_clean(raw.get("season")),
        occasion=_clean(raw.get("occasion")),
        brand=_clean(raw.get("brand")),
        price=raw.get("price"),
        currency=_clean(raw.get("currency")),
        stock_status=_clean(raw.get("stock_status")),
        metadata_source=metadata_source,
        extra={k: v for k, v in raw.items() if k not in {"item_id", "id"}},
    )


def normalize_polyvore_items(raws: Iterable[Dict[str, Any]]) -> List[NormalizedItem]:
    return [normalize_polyvore_item(r) for r in raws]
