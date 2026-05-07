"""Approach 4 runner — prompt-controllable.

Qwen prompt parser -> GR-Lite / FashionSigLIP embedder -> Qdrant retrieval
with constraint-aware filters -> constrained Text2Outfit composer
-> MEDAL / VICTOR reranker -> Qwen explainer.
"""
from __future__ import annotations

from dataclasses import asdict

from src.api import OutfitPipeline, PipelineConfig
from src.common import NormalizedItem
from src.composition.text2outfit_composer import Text2OutfitComposer
from src.composition.text2outfit_constrained import ConstrainedText2OutfitComposer
from src.embeddings.gr_lite import GRLiteEmbedder
from src.explanation import QwenExplainer
from src.parsers.constraint_schema import PromptConstraints
from src.parsers.qwen_prompt_parser import QwenPromptParser
from src.reranking import MedalReranker
from src.retrieval import QdrantRetriever
from src.vectorstore import QdrantStore


def build_pipeline(
    qwen_client,
    embed_model,
    embed_processor,
    qdrant_client,
    text2outfit_client,
    medal_model,
    collection: str = "items_approach4",
    vector_size: int = 768,
) -> OutfitPipeline:
    store = QdrantStore(qdrant_client, collection=collection, vector_size=vector_size)
    embedder = GRLiteEmbedder(embed_model, embed_processor)
    composer = ConstrainedText2OutfitComposer(Text2OutfitComposer(text2outfit_client))
    return OutfitPipeline(
        parser=None,  # prompt parsing runs via `run_with_prompt` below
        retriever=QdrantRetriever(store, embedder),
        composer=composer,
        reranker=MedalReranker(medal_model),
        explainer=QwenExplainer(qwen_client),
        config=PipelineConfig(per_slot_top_k=25, top_final=3),
    )


def constraints_to_filters(pc: PromptConstraints) -> dict:
    filters: dict = {}
    if pc.season:
        filters["season"] = pc.season
    return filters


def run_with_prompt(
    pipeline: OutfitPipeline,
    prompt_parser: QwenPromptParser,
    seed_item: NormalizedItem,
    user_prompt: str,
) -> list:
    pc = prompt_parser.parse_prompt(seed_item, user_prompt)
    constraints = {
        "prompt_constraints": pc,
        "retrieval_filters": constraints_to_filters(pc),
        "prompt_summary": asdict(pc),
    }
    return pipeline.run(seed_item, constraints=constraints)
