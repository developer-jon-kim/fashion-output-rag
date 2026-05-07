"""MEDAL compatibility reranker (Approaches 1, 3, and 4)."""
from __future__ import annotations

from typing import List, Optional

from src.common import OutfitCandidate, Reranker


class MedalReranker(Reranker):
    def __init__(self, model):
        self.model = model

    def _score_outfit(self, outfit: OutfitCandidate, context: Optional[dict]) -> float:
        return float(self.model.score(outfit.item_ids, context=context))

    def score(
        self,
        outfits: List[OutfitCandidate],
        context: Optional[dict] = None,
    ) -> List[OutfitCandidate]:
        for outfit in outfits:
            outfit.rerank_score = self._score_outfit(outfit, context)
        return outfits
