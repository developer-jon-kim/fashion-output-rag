"""Text2Outfit composer wrapper (Approach 1 and 4).

Asks the composition model to decide which slots to fill for a given seed
item and optional user constraints, then hands off to `assemble_outfits`.
"""
from __future__ import annotations

from typing import Dict, List, Optional

from src.common import Composer, NormalizedItem, OutfitCandidate
from .outfit_assembler import assemble_outfits


class Text2OutfitComposer(Composer):
    def __init__(self, client, model: str = "text2outfit"):
        self.client = client
        self.model = model

    def plan(
        self,
        seed_item: NormalizedItem,
        constraints: Optional[dict] = None,
    ) -> Dict[str, List[str]]:
        plan = self.client.plan(
            model=self.model,
            seed={
                "item_id": seed_item.item_id,
                "slot": seed_item.slot,
                "subcategory": seed_item.subcategory,
                "title": seed_item.title,
            },
            constraints=constraints or {},
        )
        return {
            "required": list(plan.get("required_slots", [])),
            "optional": list(plan.get("optional_slots", [])),
            "style_constraints": plan.get("style_constraints", {}),
        }

    def compose(
        self,
        seed_item: NormalizedItem,
        retrieved_by_slot: Dict[str, list],
        constraints: Optional[dict] = None,
    ) -> List[OutfitCandidate]:
        plan = self.plan(seed_item, constraints)
        return assemble_outfits(
            seed_item=seed_item,
            required_slots=plan["required"],
            optional_slots=plan.get("optional", []),
            retrieved_by_slot=retrieved_by_slot,
        )
