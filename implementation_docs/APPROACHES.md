# Approaches Index

This file maps the four proposed implementation approaches to concrete documents.

## Available approaches

1. **Approach 1 — Highest-ceiling / best projected outcome**
   - File: [`APPROACH_1_HIGHEST_CEILING.md`](./APPROACH_1_HIGHEST_CEILING.md)
   - Stack:
     - Qwen2.5-VL for structured parsing
     - Fashion SigLIP 2 for dense retrieval
     - Qdrant hybrid retrieval
     - Text2Outfit for composition
     - MEDAL for reranking
     - Qwen2.5-VL for explanation

2. **Approach 2 — Best fully open**
   - File: [`APPROACH_2_FULLY_OPEN.md`](./APPROACH_2_FULLY_OPEN.md)
   - Stack:
     - Qwen2.5-VL for structured parsing
     - GR-Lite or Marqo FashionSigLIP for dense retrieval
     - Qdrant hybrid retrieval
     - Template-based composition first, optional learned composition later
     - OutfitTransformer or VICTOR for reranking
     - Qwen2.5-VL for explanation

3. **Approach 3 — Best production-first**
   - File: [`APPROACH_3_PRODUCTION_FIRST.md`](./APPROACH_3_PRODUCTION_FIRST.md)
   - Stack:
     - Source taxonomy + Qwen2.5-VL fallback for structured parsing
     - Marqo FashionSigLIP or OpenFashionCLIP for dense retrieval
     - Qdrant hybrid retrieval with strict payload filters
     - Template-based composition
     - MEDAL reranking
     - Qwen2.5-VL for explanation

4. **Approach 4 — Best prompt-controllable**
   - File: [`APPROACH_4_PROMPT_CONTROLLABLE.md`](./APPROACH_4_PROMPT_CONTROLLABLE.md)
   - Stack:
     - Qwen2.5-VL as parser/controller
     - FashionSigLIP or GR-Lite for retrieval
     - Qdrant hybrid retrieval
     - Text2Outfit for prompt-aware composition
     - MEDAL or VICTOR for reranking
     - Qwen2.5-VL for explanation

## How these relate to the main docs

- `README.md` = shared architecture pattern used across all approaches
- `PLANNING.md` = generic implementation order
- `docs/IMPLEMENTATION_GUIDE.md` = common pipeline steps
- the `APPROACH_*` docs = approach-specific model choices and implementation differences

## Suggested implementation order if you want to build all of them

1. Build the shared foundation once:
   - loaders
   - normalization
   - metadata fallback
   - Qdrant integration
   - retrieval interface
   - composition interface
   - reranker interface
   - explanation interface
2. Start with **Approach 3** or **Approach 2** as the easiest baselines.
3. Add **Approach 4** if prompt control matters.
4. Add **Approach 1** last if you can access the strongest models.

## Shared interfaces

All approaches should conform to the same interfaces so you can swap them:

- `MetadataParser`
- `Embedder`
- `Retriever`
- `Composer`
- `Reranker`
- `Explainer`

That way, each approach is mainly a configuration change plus a few model-specific wrappers.
