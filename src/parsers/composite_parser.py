"""Chain multiple parsers left-to-right (Approach 3: taxonomy -> Qwen fallback)."""
from __future__ import annotations

from typing import List

from src.common import MetadataParser, NormalizedItem


class CompositeParser(MetadataParser):
    def __init__(self, parsers: List[MetadataParser]):
        self.parsers = parsers

    def parse(self, item: NormalizedItem) -> NormalizedItem:
        for parser in self.parsers:
            item = parser.parse(item)
        return item
