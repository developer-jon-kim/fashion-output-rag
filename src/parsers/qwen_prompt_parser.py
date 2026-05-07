"""Turn free-text user prompts into `PromptConstraints` (Approach 4)."""
from __future__ import annotations

import json

from src.common import NormalizedItem
from .constraint_schema import PromptConstraints


SYSTEM_PROMPT = """Convert the user's outfit request into strict JSON with keys:
occasion, season, color_preferences, style_keywords, budget_preference,
required_slots, forbidden_slots. Use null or [] when unspecified.
"""


class QwenPromptParser:
    def __init__(self, client, model: str = "qwen2.5-vl"):
        self.client = client
        self.model = model

    def parse_prompt(self, seed_item: NormalizedItem, prompt: str) -> PromptConstraints:
        payload = {
            "seed": {
                "item_id": seed_item.item_id,
                "slot": seed_item.slot,
                "title": seed_item.title,
            },
            "prompt": prompt,
        }
        raw = self.client.generate(
            model=self.model,
            system=SYSTEM_PROMPT,
            user=json.dumps(payload),
        )
        try:
            data = json.loads(raw)
        except Exception:
            data = {}
        return PromptConstraints(
            occasion=data.get("occasion"),
            season=data.get("season"),
            color_preferences=list(data.get("color_preferences") or []),
            style_keywords=list(data.get("style_keywords") or []),
            budget_preference=data.get("budget_preference"),
            required_slots=list(data.get("required_slots") or []),
            forbidden_slots=list(data.get("forbidden_slots") or []),
        )
