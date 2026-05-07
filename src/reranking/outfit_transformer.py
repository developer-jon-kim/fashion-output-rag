"""OutfitTransformer reranker (Approach 2)."""
from __future__ import annotations

from typing import List, Optional

from src.common import OutfitCandidate, Reranker


class OutfitTransformerReranker(Reranker):
    def __init__(self, model):
        self.model = model

    def score(
        self,
        outfits: List[OutfitCandidate],
        context: Optional[dict] = None,
    ) -> List[OutfitCandidate]:
        for outfit in outfits:
            outfit.rerank_score = float(self.model.score(outfit.item_ids))
        return outfits
