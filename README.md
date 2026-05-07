# Outfit Pipeline

A modular fashion outfit recommendation system. Given a seed item, it retrieves complementary pieces, assembles complete outfit candidates, reranks them for compatibility, and generates short explanations for the top picks.

The repo ships **four interchangeable approach configurations** that share a common pipeline interface, so you can swap parsers, embedders, composers, and rerankers without touching orchestration code.

## Architecture

```
seed item
  → structured parsing       (Qwen2.5-VL or taxonomy mapper)
  → slot planning            (template or Text2Outfit)
  → slot-aware retrieval     (fashion embedding + Qdrant, optional filters)
  → outfit assembly          (cartesian over required slots)
  → compatibility reranking  (MEDAL / OutfitTransformer / VICTOR)
  → explanation              (Qwen2.5-VL)
```

All approaches conform to the same interfaces — `MetadataParser`, `Embedder`, `Retriever`, `Composer`, `Reranker`, `Explainer` — defined in [src/common/interfaces.py](src/common/interfaces.py). The shared orchestration lives in [src/api/pipeline.py](src/api/pipeline.py).

## The four approaches

| # | Focus | Parser | Embedder | Composer | Reranker | Runner |
|---|---|---|---|---|---|---|
| 1 | Highest-ceiling | Qwen2.5-VL | Fashion SigLIP 2 | Text2Outfit | MEDAL | [scripts/run_approach_1.py](scripts/run_approach_1.py) |
| 2 | Fully open | Qwen2.5-VL | Marqo FashionSigLIP | Template | OutfitTransformer | [scripts/run_approach_2.py](scripts/run_approach_2.py) |
| 3 | Production-first | Taxonomy + Qwen fallback | Marqo FashionSigLIP | Template | MEDAL | [scripts/run_approach_3.py](scripts/run_approach_3.py) |
| 4 | Prompt-controllable | Qwen prompt parser | GR-Lite | Constrained Text2Outfit | MEDAL | [scripts/run_approach_4.py](scripts/run_approach_4.py) |

All four use Qdrant for vector storage and Qwen2.5-VL for explanations. See [implementation_docs/APPROACHES.md](implementation_docs/APPROACHES.md) for the full breakdown.

## Repo layout

```
src/
  api/             OutfitPipeline orchestration
  common/          shared interfaces and schemas
  parsers/         metadata extraction (Qwen, taxonomy, prompt)
  embeddings/      fashion embedders (SigLIP variants, GR-Lite, OpenFashionCLIP)
  retrieval/       Qdrant-backed slot-aware retriever
  vectorstore/     Qdrant client wrapper
  composition/     slot planning + outfit assembly (template / Text2Outfit)
  reranking/       MEDAL, OutfitTransformer, VICTOR
  explanation/     Qwen explainer
  normalization/   Polyvore → internal schema, slot mapping
  loaders/         dataset loaders
  evaluation/      offline metrics
scripts/           per-approach runners
implementation_docs/   approach-specific docs
fashion_outfit_pipeline_docs/   shared architecture docs
```

## Quick start

The runners are wrappers — they take pre-loaded models/clients and wire them into a pipeline. Loading the underlying ML models (Qwen, SigLIP, MEDAL, etc.) is left to the caller.

```python
from scripts.run_approach_3 import build_pipeline

pipeline = build_pipeline(
    qwen_client=...,           # your Qwen2.5-VL client
    embed_model=...,           # Marqo FashionSigLIP model
    embed_processor=...,       # matching processor
    qdrant_client=...,         # qdrant_client.QdrantClient(...)
    medal_model=...,           # MEDAL scorer
)

outfits = pipeline.run(seed_item)
```

## Datasets

Prototype against:
- `owj0421/polyvore` — searchable catalog
- `owj0421/polyvore-outfits` — outfit-level supervision

Loaders live in [src/loaders/](src/loaders/). Normalization to the internal schema is in [src/normalization/normalize_polyvore.py](src/normalization/normalize_polyvore.py).

## Documentation

- [implementation_docs/APPROACHES.md](implementation_docs/APPROACHES.md) — the four approaches in detail
- [implementation_docs/IMPLEMENTATION_GUIDE.md](implementation_docs/IMPLEMENTATION_GUIDE.md) — pipeline build steps
- [implementation_docs/STEP_BY_STEP_CODING_EACH_APPROACH.md](implementation_docs/STEP_BY_STEP_CODING_EACH_APPROACH.md) — per-approach coding walkthrough
- [fashion_outfit_pipeline_docs/](fashion_outfit_pipeline_docs/) — shared architecture, datasets, evaluation, team workflow

## Design principles

1. **Don't make one model do everything.** Specialized components for parsing, retrieval, ranking, and explanation.
2. **Trust metadata before vision.** If a field exists in source data, use it before inferring.
3. **Retrieve narrowly, rerank deeply.** Strict slot/category filters early; expensive scoring only on strong candidates.
4. **Prototype on Polyvore, abstract the schema.** Swap in real client data later without touching the core pipeline.
5. **Keep a metadata fallback path.** Client data is often incomplete.

## Status

Adapter/wrapper implementations for every component are in place across all four approaches. Heavy ML models are dependency-injected — model loading is not bundled. `configs/` is empty (per-approach config files are TODO).
