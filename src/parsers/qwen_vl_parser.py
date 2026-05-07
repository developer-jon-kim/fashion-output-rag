"""Qwen2.5-VL structured metadata parser (Approach 1).

Fills missing fields from image + title + description + raw_category.
Wrap the actual model call in `_call_qwen`; the fill-only logic above is
shared and should not be duplicated per approach.
"""
from __future__ import annotations

import json
from typing import Any, Dict

from src.common import MetadataParser, NormalizedItem

FILLABLE_FIELDS = (
    "slot",
    "subcategory",
    "colors",
    "material",
    "pattern",
    "season",
    "occasion",
    "department",
)

PROMPT = """You are a fashion catalog metadata extractor.
Return strict JSON with keys: slot, subcategory, colors, material, pattern,
season, occasion, department, canonical_title.
Use null for unknown values.
"""


class QwenVLParser(MetadataParser):
    def __init__(self, client, model: str = "qwen2.5-vl"):
        self.client = client
        self.model = model

    def _call_qwen(self, item: NormalizedItem) -> Dict[str, Any]:
        user_payload = {
            "image": item.image_path_or_url,
            "title": item.title,
            "description": item.description,
            "raw_category": item.raw_category,
        }
        raw = self.client.generate(
            model=self.model,
            system=PROMPT,
            user=json.dumps(user_payload),
        )
        try:
            return json.loads(raw)
        except Exception:
            return {}

    def parse(self, item: NormalizedItem) -> NormalizedItem:
        missing = [f for f in FILLABLE_FIELDS if not getattr(item, f, None)]
        if not missing:
            return item
        inferred = self._call_qwen(item)
        for field in missing:
            value = inferred.get(field)
            if value in (None, "", []):
                continue
            setattr(item, field, value)
            item.metadata_source[field] = "qwen"
        if not item.title and inferred.get("canonical_title"):
            item.title = inferred["canonical_title"]
            item.metadata_source["title"] = "qwen"
        return item
