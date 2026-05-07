"""Qwen2.5-VL explanation generator (shared by all four approaches)."""
from __future__ import annotations

from typing import Optional

from src.common import Explainer, OutfitCandidate


SYSTEM_PROMPT = """You explain fashion outfits in one or two short sentences.
Mention style compatibility, color harmony, and occasion alignment.
Do not invent facts that are not given.
"""


class QwenExplainer(Explainer):
    def __init__(self, client, model: str = "qwen2.5-vl"):
        self.client = client
        self.model = model

    def explain(self, outfit: OutfitCandidate, context: Optional[dict] = None) -> str:
        payload = {
            "seed_item_id": outfit.seed_item_id,
            "slot_map": outfit.slot_map,
            "rerank_score": outfit.rerank_score,
            "context": context or {},
        }
        return self.client.generate(model=self.model, system=SYSTEM_PROMPT, user=payload)
