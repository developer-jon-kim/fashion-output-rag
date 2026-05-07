"""Build outfit candidates from per-slot retrieval pools.

Keep this stage deterministic and cheap; the reranker decides the winners.
"""
from __future__ import annotations

from itertools import product
from typing import Dict, List

from src.common import NormalizedItem, OutfitCandidate


def _result_id(r) -> str:
    return str(getattr(r, "id", None) or getattr(r, "item_id", None))


def _result_score(r) -> float:
    return float(getattr(r, "score", 0.0) or 0.0)


def assemble_outfits(
    seed_item: NormalizedItem,
    required_slots: List[str],
    optional_slots: List[str],
    retrieved_by_slot: Dict[str, list],
    per_slot_top_n: int = 5,
    max_candidates: int = 50,
) -> List[OutfitCandidate]:
    pools: List[List] = []
    slot_order: List[str] = []
    for slot in required_slots:
        results = retrieved_by_slot.get(slot, [])[:per_slot_top_n]
        if not results:
            return []
        pools.append(results)
        slot_order.append(slot)

    outfits: List[OutfitCandidate] = []
    seen = set()
    for combo in product(*pools):
        ids = tuple(_result_id(r) for r in combo)
        if len(set(ids)) != len(ids):
            continue
        key = (seed_item.item_id,) + ids
        if key in seen:
            continue
        seen.add(key)

        slot_map = {seed_item.slot or "seed": seed_item.item_id}
        retrieval_scores: Dict[str, float] = {}
        for slot, r in zip(slot_order, combo):
            rid = _result_id(r)
            slot_map[slot] = rid
            retrieval_scores[rid] = _result_score(r)

        outfits.append(
            OutfitCandidate(
                seed_item_id=seed_item.item_id,
                item_ids=[seed_item.item_id, *ids],
                slot_map=slot_map,
                retrieval_scores=retrieval_scores,
            )
        )
        if len(outfits) >= max_candidates:
            break
    return outfits
