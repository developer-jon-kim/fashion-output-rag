"""Slot-aware retrieval using the shared `QdrantStore`.

Used by all approaches. Per-approach differences (strict filters, lexical
boosts, constraint-aware filtering) are handled by passing the `filters` dict.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from src.common import NormalizedItem, Embedder, Retriever
from src.vectorstore import QdrantStore


class QdrantRetriever(Retriever):
    def __init__(self, store: QdrantStore, embedder: Embedder):
        self.store = store
        self.embedder = embedder

    def search(
        self,
        query_item: NormalizedItem,
        target_slot: str,
        top_k: int = 20,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[Any]:
        vec = self.embedder.embed_query(query_item)
        merged_filters: Dict[str, Any] = {"slot": target_slot}
        if filters:
            merged_filters.update(filters)
        results = self.store.search(vector=list(vec), top_k=top_k, filters=merged_filters)
        return [r for r in results if getattr(r, "id", None) != query_item.item_id]
