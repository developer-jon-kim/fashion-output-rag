"""Approach 2 runner — best fully open.

Qwen parser -> Marqo FashionSigLIP / GR-Lite embedder -> Qdrant retrieval
-> template composer -> OutfitTransformer / VICTOR reranker -> Qwen explainer.
"""
from __future__ import annotations

from src.api import OutfitPipeline, PipelineConfig
from src.composition import TemplateComposer
from src.embeddings.marqo_fashion_siglip import MarqoFashionSigLIPEmbedder
from src.explanation import QwenExplainer
from src.parsers import QwenVLParser
from src.reranking.outfit_transformer import OutfitTransformerReranker
from src.retrieval import QdrantRetriever
from src.vectorstore import QdrantStore


def build_pipeline(
    qwen_client,
    embed_model,
    embed_processor,
    qdrant_client,
    outfit_transformer_model,
    collection: str = "items_approach2",
    vector_size: int = 768,
) -> OutfitPipeline:
    store = QdrantStore(qdrant_client, collection=collection, vector_size=vector_size)
    embedder = MarqoFashionSigLIPEmbedder(embed_model, embed_processor)
    return OutfitPipeline(
        parser=QwenVLParser(qwen_client),
        retriever=QdrantRetriever(store, embedder),
        composer=TemplateComposer(),
        reranker=OutfitTransformerReranker(outfit_transformer_model),
        explainer=QwenExplainer(qwen_client),
        config=PipelineConfig(per_slot_top_k=20, top_final=3),
    )
