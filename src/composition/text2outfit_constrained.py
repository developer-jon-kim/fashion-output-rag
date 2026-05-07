"""Constraint-aware Text2Outfit composer (Approach 4).

Takes parsed `PromptConstraints` and produces outfit candidates that respect
forbidden slots and favor requested style keywords.
"""
from __future__ import annotations

from typing import Dict, List, Optional

from src.common import Composer, NormalizedItem, OutfitCandidate
from src.parsers.constraint_schema import PromptConstraints
from .outfit_assembler import assemble_outfits
from .text2outfit_composer import Text2OutfitComposer


class ConstrainedText2OutfitComposer(Composer):
    def __init__(self, base: Text2OutfitComposer):
        self.base = base

    def plan(
        self,
        seed_item: NormalizedItem,
        constraints: Optional[dict] = None,
    ) -> Dict[str, List[str]]:
        plan = self.base.plan(seed_item, constraints=constraints)
        pc: Optional[PromptConstraints] = (constraints or {}).get("prompt_constraints")
        if pc:
            for slot in pc.required_slots:
                if slot not in plan["required"]:
                    plan["required"].append(slot)
            plan["required"] = [s for s in plan["required"] if s not in pc.forbidden_slots]
            plan["optional"] = [s for s in plan.get("optional", []) if s not in pc.forbidden_slots]
        return plan

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
