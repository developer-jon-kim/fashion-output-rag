"""Prompt constraint schema (Approach 4)."""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class PromptConstraints:
    occasion: str | None = None
    season: str | None = None
    color_preferences: list[str] = field(default_factory=list)
    style_keywords: list[str] = field(default_factory=list)
    budget_preference: str | None = None
    required_slots: list[str] = field(default_factory=list)
    forbidden_slots: list[str] = field(default_factory=list)
