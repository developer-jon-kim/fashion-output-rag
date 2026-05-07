from typing import List, Dict, Optional
from .schemas import NormalizedItem, OutfitCandidate


class MetadataParser:
    def parse(self, item: NormalizedItem) -> NormalizedItem:
        raise NotImplementedError


class Embedder:
    def embed_item(self, item: NormalizedItem):
        raise NotImplementedError

    def embed_query(self, item: NormalizedItem):
        return self.embed_item(item)


class Retriever:
    def search(
        self,
        query_item: NormalizedItem,
        target_slot: str,
        top_k: int = 20,
        filters: Optional[dict] = None,
    ):
        raise NotImplementedError


class Composer:
    def compose(
        self,
        seed_item: NormalizedItem,
        retrieved_by_slot: Dict[str, list],
        constraints: Optional[dict] = None,
    ) -> List[OutfitCandidate]:
        raise NotImplementedError


class Reranker:
    def score(
        self,
        outfits: List[OutfitCandidate],
        context: Optional[dict] = None,
    ) -> List[OutfitCandidate]:
        raise NotImplementedError


class Explainer:
    def explain(
        self,
        outfit: OutfitCandidate,
        context: Optional[dict] = None,
    ) -> str:
        raise NotImplementedError
