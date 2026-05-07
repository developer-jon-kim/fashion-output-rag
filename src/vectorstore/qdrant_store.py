"""Qdrant collection setup and helpers.

Kept thin so retrievers can be swapped without touching store code.
"""
from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional

from src.common import NormalizedItem


PAYLOAD_FIELDS = (
    "item_id",
    "slot",
    "subcategory",
    "department",
    "season",
    "brand",
    "price",
    "stock_status",
)


class QdrantStore:
    def __init__(self, client, collection: str, vector_size: int, distance: str = "Cosine"):
        self.client = client
        self.collection = collection
        self.vector_size = vector_size
        self.distance = distance

    def create_collection(self) -> None:
        from qdrant_client.http import models as qm

        self.client.recreate_collection(
            collection_name=self.collection,
            vectors_config=qm.VectorParams(size=self.vector_size, distance=self.distance),
        )

    def _payload(self, item: NormalizedItem) -> Dict[str, Any]:
        return {f: getattr(item, f, None) for f in PAYLOAD_FIELDS}

    def upsert(self, items: Iterable[NormalizedItem], vectors: Iterable[List[float]]) -> None:
        from qdrant_client.http import models as qm

        points = [
            qm.PointStruct(id=item.item_id, vector=list(vec), payload=self._payload(item))
            for item, vec in zip(items, vectors)
        ]
        self.client.upsert(collection_name=self.collection, points=points)

    def search(
        self,
        vector: List[float],
        top_k: int = 20,
        filters: Optional[Dict[str, Any]] = None,
    ):
        from qdrant_client.http import models as qm

        must = []
        for key, value in (filters or {}).items():
            if value is None:
                continue
            if isinstance(value, list):
                must.append(qm.FieldCondition(key=key, match=qm.MatchAny(any=value)))
            else:
                must.append(qm.FieldCondition(key=key, match=qm.MatchValue(value=value)))
        q_filter = qm.Filter(must=must) if must else None
        return self.client.search(
            collection_name=self.collection,
            query_vector=vector,
            query_filter=q_filter,
            limit=top_k,
        )
