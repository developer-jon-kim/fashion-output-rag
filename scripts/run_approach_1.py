"""Approach 1 runner — highest-ceiling stack.

Qwen2.5-VL parser -> Fashion SigLIP 2 embedder -> Qdrant retrieval
-> Text2Outfit composer -> MEDAL reranker -> Qwen2.5-VL explainer.
"""
from __future__ import annotations

from src.api import OutfitPipeline, PipelineConfig
from src.common import NormalizedItem
from src.composition.text2outfit_composer import Text2OutfitComposer
from src.embeddings.fashion_siglip2 import FashionSigLIP2Embedder
from src.explanation import QwenExplainer
from src.parsers import QwenVLParser
from src.reranking import MedalReranker
from src.retrieval import QdrantRetriever
from src.vectorstore import QdrantStore


def build_pipeline(
    qwen_client,
    siglip_model,
    siglip_processor,
    qdrant_client,
    text2outfit_client,
    medal_model,
    collection: str = "items_approach1",
    vector_size: int = 1152,
) -> OutfitPipeline:
    store = QdrantStore(qdrant_client, collection=collection, vector_size=vector_size)
    embedder = FashionSigLIP2Embedder(siglip_model, siglip_processor)
    return OutfitPipeline(
        parser=QwenVLParser(qwen_client),
        retriever=QdrantRetriever(store, embedder),
        composer=Text2OutfitComposer(text2outfit_client),
        reranker=MedalReranker(medal_model),
        explainer=QwenExplainer(qwen_client),
        config=PipelineConfig(per_slot_top_k=20, top_final=3),
    )


def main(seed_item: NormalizedItem, pipeline: OutfitPipeline) -> list:
    return pipeline.run(seed_item)
