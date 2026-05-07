"""Fashion SigLIP 2 embedder wrapper (Approach 1)."""
from __future__ import annotations

from typing import List

from src.common import Embedder, NormalizedItem


def build_text_input(item: NormalizedItem) -> str:
    return (
        f"{item.title or ''}. category: {item.slot or ''}. "
        f"subcategory: {item.subcategory or ''}. description: {item.description or ''}"
    ).strip()


class FashionSigLIP2Embedder(Embedder):
    def __init__(self, model, processor):
        self.model = model
        self.processor = processor

    def _encode(self, item: NormalizedItem) -> List[float]:
        text = build_text_input(item)
        inputs = self.processor(
            images=item.image_path_or_url,
            text=text,
            return_tensors="pt",
            padding=True,
        )
        outputs = self.model(**inputs)
        vec = outputs.get("image_embeds") or outputs.get("pooler_output")
        return vec[0].detach().cpu().tolist()

    def embed_item(self, item: NormalizedItem) -> List[float]:
        return self._encode(item)
