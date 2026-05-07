"""VICTOR reranker (Approaches 2 and 4)."""
from __future__ import annotations

from typing import List, Optional

from src.common import OutfitCandidate, Reranker


class VictorReranker(Reranker):
    def __init__(self, model):
        self.model = model

    def score(
        self,
        outfits: List[OutfitCandidate],
        context: Optional[dict] = None,
    ) -> List[OutfitCandidate]:
        for outfit in outfits:
            outfit.rerank_score = float(self.model.score(outfit.item_ids, context=context))
        return outfits
