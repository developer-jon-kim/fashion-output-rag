"""Approach 3 runner — production-first.

Taxonomy-mapped parsing with conservative Qwen fallback,
Marqo FashionSigLIP / OpenFashionCLIP embedder, Qdrant retrieval with strict
payload filters, template composer, MEDAL reranker, Qwen explainer.
"""
from __future__ import annotations

from src.api import OutfitPipeline, PipelineConfig
from src.composition import TemplateComposer
from src.embeddings.marqo_fashion_siglip import MarqoFashionSigLIPEmbedder
from src.explanation import QwenExplainer
from src.parsers.composite_parser import CompositeParser
from src.parsers.qwen_fallback_parser import QwenFallbackParser
from src.parsers.qwen_vl_parser import QwenVLParser
from src.parsers.taxonomy_mapper import TaxonomyMapper
from src.reranking import MedalReranker
from src.retrieval import QdrantRetriever
from src.vectorstore import QdrantStore


def build_pipeline(
    qwen_client,
    embed_model,
    embed_processor,
    qdrant_client,
    medal_model,
    collection: str = "items_approach3",
    vector_size: int = 768,
) -> OutfitPipeline:
    store = QdrantStore(qdrant_client, collection=collection, vector_size=vector_size)
    embedder = MarqoFashionSigLIPEmbedder(embed_model, embed_processor)
    parser = CompositeParser(
        [
            TaxonomyMapper(),
            QwenFallbackParser(QwenVLParser(qwen_client)),
        ]
    )
    return OutfitPipeline(
        parser=parser,
        retriever=QdrantRetriever(store, embedder),
        composer=TemplateComposer(),
        reranker=MedalReranker(medal_model),
        explainer=QwenExplainer(qwen_client),
        config=PipelineConfig(per_slot_top_k=20, top_final=3),
    )


STRICT_FILTERS_EXAMPLE = {
    "retrieval_filters": {
        "stock_status": "in_stock",
        "department": None,
        "season": None,
    }
}
