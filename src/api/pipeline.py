"""Shared outfit pipeline.

This is the common pipeline used by every approach (IMPLEMENTATION_GUIDE steps
7–11). Each approach supplies its own parser / embedder / composer / reranker
/ explainer; the orchestration is identical.

Pipeline order:
    1. (optional) structured parsing fills missing fields
    2. composer produces slot plan
    3. retriever pulls candidates per required slot
    4. assembler builds outfit candidates
    5. reranker scores and sorts
    6. explainer narrates top-k
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional

from src.common import (
    NormalizedItem,
    OutfitCandidate,
    MetadataParser,
    Retriever,
    Composer,
    Reranker,
    Explainer,
)


@dataclass
class PipelineConfig:
    per_slot_top_k: int = 20
    top_final: int = 3
    explain_top_k: int = 3


class OutfitPipeline:
    def __init__(
        self,
        parser: Optional[MetadataParser],
        retriever: Retriever,
        composer: Composer,
        reranker: Reranker,
        explainer: Explainer,
        config: Optional[PipelineConfig] = None,
    ):
        self.parser = parser
        self.retriever = retriever
        self.composer = composer
        self.reranker = reranker
        self.explainer = explainer
        self.config = config or PipelineConfig()

    def run(
        self,
        seed_item: NormalizedItem,
        constraints: Optional[dict] = None,
    ) -> List[OutfitCandidate]:
        if self.parser is not None:
            seed_item = self.parser.parse(seed_item)

        plan = self._plan_slots(seed_item, constraints)
        retrieved_by_slot = self._retrieve(seed_item, plan, constraints)

        outfits = self.composer.compose(
            seed_item=seed_item,
            retrieved_by_slot=retrieved_by_slot,
            constraints=constraints,
        )
        if not outfits:
            return []

        outfits = self.reranker.score(outfits, context=constraints)
        outfits = sorted(
            outfits,
            key=lambda o: (o.rerank_score is not None, o.rerank_score or 0.0),
            reverse=True,
        )[: self.config.top_final]

        for outfit in outfits[: self.config.explain_top_k]:
            outfit.explanation = self.explainer.explain(outfit, context=constraints)
        return outfits

    def _plan_slots(self, seed_item: NormalizedItem, constraints: Optional[dict]) -> List[str]:
        if hasattr(self.composer, "plan"):
            plan = self.composer.plan(seed_item)
            if isinstance(plan, dict):
                return list(plan.get("required", [])) + list(plan.get("optional", []))
            return list(plan)
        return ["bottom", "shoes"]

    def _retrieve(
        self,
        seed_item: NormalizedItem,
        slots: List[str],
        constraints: Optional[dict],
    ) -> Dict[str, list]:
        filters = (constraints or {}).get("retrieval_filters") or {}
        out: Dict[str, list] = {}
        for slot in slots:
            out[slot] = self.retriever.search(
                query_item=seed_item,
                target_slot=slot,
                top_k=self.config.per_slot_top_k,
                filters=filters,
            )
        return out
