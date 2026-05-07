"""Deterministic template-based composition.

Shared by Approach 2 (primary) and Approach 3 (primary). Approaches 1 and 4
use a learned/LLM composer (`text2outfit_composer.py`).
"""
from __future__ import annotations

from typing import Dict, List, Optional

from src.common import Composer, NormalizedItem, OutfitCandidate


SLOT_TEMPLATES: Dict[str, Dict[str, List[str]]] = {
    "top": {"required": ["bottom", "shoes"], "optional": ["outerwear", "accessory"]},
    "dress": {"required": ["shoes"], "optional": ["outerwear", "accessory"]},
    "outerwear": {"required": ["top", "bottom", "shoes"], "optional": ["accessory"]},
    "bottom": {"required": ["top", "shoes"], "optional": ["outerwear", "accessory"]},
    "shoes": {"required": ["top", "bottom"], "optional": ["outerwear", "accessory"]},
}


class TemplateComposer(Composer):
    def __init__(self, templates: Optional[Dict[str, Dict[str, List[str]]]] = None):
        self.templates = templates or SLOT_TEMPLATES

    def plan(self, seed_item: NormalizedItem) -> Dict[str, List[str]]:
        slot = seed_item.slot or "top"
        return self.templates.get(slot, self.templates["top"])

    def compose(
        self,
        seed_item: NormalizedItem,
        retrieved_by_slot: Dict[str, list],
        constraints: Optional[dict] = None,
    ) -> List[OutfitCandidate]:
        from .outfit_assembler import assemble_outfits

        plan = self.plan(seed_item)
        return assemble_outfits(
            seed_item=seed_item,
            required_slots=plan["required"],
            optional_slots=plan.get("optional", []),
            retrieved_by_slot=retrieved_by_slot,
        )
