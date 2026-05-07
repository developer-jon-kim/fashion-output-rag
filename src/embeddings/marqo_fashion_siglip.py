"""Marqo FashionSigLIP embedder (Approaches 2 and 3)."""
from __future__ import annotations

from typing import List

from src.common import Embedder, NormalizedItem
from .fashion_siglip2 import build_text_input


class MarqoFashionSigLIPEmbedder(Embedder):
    def __init__(self, model, processor):
        self.model = model
        self.processor = processor

    def embed_item(self, item: NormalizedItem) -> List[float]:
        inputs = self.processor(
            images=item.image_path_or_url,
            text=build_text_input(item),
            return_tensors="pt",
            padding=True,
        )
        outputs = self.model(**inputs)
        vec = outputs.get("image_embeds") or outputs.get("pooler_output")
        return vec[0].detach().cpu().tolist()
