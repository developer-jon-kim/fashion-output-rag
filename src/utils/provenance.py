"""Provenance tracking for normalized item fields.

Used by production-first Approach 3 to ensure every inferred field can be
traced back to whether it came from source metadata, page parsing, Qwen
inference, or retrieval consensus.
"""
from __future__ import annotations

from src.common import NormalizedItem

SOURCE_METADATA = "source"
PAGE_PARSE = "page_parse"
TEXT_INFERENCE = "text_inference"
QWEN_INFERENCE = "qwen"
RETRIEVAL_CONSENSUS = "retrieval_consensus"


def mark(item: NormalizedItem, field: str, origin: str) -> None:
    item.metadata_source[field] = origin


def is_missing(item: NormalizedItem, field: str) -> bool:
    val = getattr(item, field, None)
    if val is None:
        return True
    if isinstance(val, (list, str)) and len(val) == 0:
        return True
    return False
