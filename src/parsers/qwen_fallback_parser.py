"""Conservative Qwen fallback (Approach 3).

Only invoked when required fields are missing after taxonomy mapping, and
never overwrites trusted source fields.
"""
from __future__ import annotations

from typing import Iterable

from src.common import MetadataParser, NormalizedItem
from src.utils.provenance import is_missing, mark, QWEN_INFERENCE
from .qwen_vl_parser import QwenVLParser


REQUIRED_FIELDS = ("slot", "subcategory", "season", "occasion")


class QwenFallbackParser(MetadataParser):
    def __init__(
        self,
        qwen_parser: QwenVLParser,
        required_fields: Iterable[str] = REQUIRED_FIELDS,
    ):
        self.qwen_parser = qwen_parser
        self.required_fields = tuple(required_fields)

    def parse(self, item: NormalizedItem) -> NormalizedItem:
        still_missing = [f for f in self.required_fields if is_missing(item, f)]
        if not still_missing:
            return item

        before = {f: getattr(item, f, None) for f in self.required_fields}
        item = self.qwen_parser.parse(item)

        for field in self.required_fields:
            if before[field] not in (None, "", []):
                setattr(item, field, before[field])
            elif getattr(item, field, None) not in (None, "", []):
                mark(item, field, QWEN_INFERENCE)
        return item
