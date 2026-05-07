# Fashion Outfit Recommendation Pipeline

This repository documentation set is designed to help a team implement the outfit recommendation system step by step.

The target architecture is:

1. **Structured parsing**
   - Use **Qwen2.5-VL** to extract or normalize product metadata.
2. **Hybrid retrieval**
   - Use a **fashion-specific embedding model** and store vectors in **Qdrant**.
   - Combine dense retrieval with keyword / metadata filtering.
3. **Outfit composition**
   - Use an outfit-composition module to decide which missing slots to fill.
4. **Compatibility reranking**
   - Use an outfit-aware reranker to score complete outfit candidates.
5. **Explanation generation**
   - Use **Qwen2.5-VL** again to generate short user-facing explanations.

For testing before real client data, use:

- `owj0421/polyvore` as the searchable product catalog
- `owj0421/polyvore-outfits` as the outfit-level supervision / evaluation set

---

## Recommended model stack

### Best projected-outcome stack
- **Structured parser / explanation model**: Qwen2.5-VL
- **Dense fashion retriever**: Fashion SigLIP 2  
  Fallbacks:
  - GR-Lite
  - Marqo FashionSigLIP
- **Vector database**: Qdrant
- **Composition model**: Text2Outfit
- **Compatibility reranker**: MEDAL  
  Fallbacks:
  - OutfitTransformer
  - VICTOR

### Best fully open stack
- **Structured parser / explanation model**: Qwen2.5-VL
- **Dense fashion retriever**: GR-Lite or Marqo FashionSigLIP
- **Vector database**: Qdrant
- **Composition model**: template-based composition first, then Text2Outfit-style fine-tuning if needed
- **Compatibility reranker**: OutfitTransformer or VICTOR

---

## What this doc set contains

- [`PLANNING.md`](./PLANNING.md): milestone plan and execution order
- [`docs/ARCHITECTURE.md`](./docs/ARCHITECTURE.md): system architecture and module responsibilities
- [`docs/DATASETS_AND_SCHEMA.md`](./docs/DATASETS_AND_SCHEMA.md): how to use Polyvore datasets and define internal schemas
- [`docs/IMPLEMENTATION_GUIDE.md`](./docs/IMPLEMENTATION_GUIDE.md): step-by-step implementation guide
- [`docs/METADATA_FALLBACK.md`](./docs/METADATA_FALLBACK.md): how to recover minimum metadata when client metadata is weak
- [`docs/EVALUATION.md`](./docs/EVALUATION.md): offline evaluation, metrics, and success criteria
- [`docs/REPO_STRUCTURE.md`](./docs/REPO_STRUCTURE.md): suggested repo/file structure
- [`docs/TEAM_WORKFLOW.md`](./docs/TEAM_WORKFLOW.md): suggested ownership split and collaboration model

---

## Core design principles

### 1. Do not make one model do everything
Use specialized components:
- Qwen for understanding and structured extraction
- a fashion embedding model for candidate retrieval
- a compatibility model for final ranking

### 2. Use metadata before vision whenever possible
If a field already exists in the data source, trust it before trying to infer it.

### 3. Retrieve narrowly, rerank deeply
Use strict slot/category filters early.
Spend the expensive scoring model only on strong candidate outfits.

### 4. Build with test data first
Use Polyvore to validate:
- indexing
- retrieval
- slot-aware candidate generation
- outfit assembly
- reranking
- evaluation

### 5. Keep a metadata fallback path
Assume client data will sometimes be incomplete.
Design a recovery path for the minimum fields needed for retrieval.

---

## Minimum fields required per item

For the algorithm to work well, each product record should ideally have:

- `item_id`
- `image`
- `title`
- `category_or_slot`
- `description` (optional but helpful)

For production usage, add if available:
- `department_or_fit_regime`
- `price`
- `currency`
- `stock_status`
- `brand`
- `material`
- `color`

When these are missing, use the metadata fallback flow described in [`docs/METADATA_FALLBACK.md`](./docs/METADATA_FALLBACK.md).

---

## End-to-end flow

```text
Product record
  -> metadata normalization
  -> Qwen structured parsing / cleanup
  -> embedding generation
  -> Qdrant indexing
  -> slot-aware retrieval for missing outfit pieces
  -> outfit candidate assembly
  -> compatibility reranking
  -> final explanation generation
  -> API response
```

---

## Suggested implementation order

1. Build dataset loaders
2. Normalize item schema
3. Stand up Qdrant and dense indexing
4. Build slot-aware retrieval
5. Build outfit assembly
6. Add compatibility reranking
7. Add explanation layer
8. Wrap in API
9. Add logging, evaluation, and dashboards

See [`PLANNING.md`](./PLANNING.md) for the full milestone plan.

---

## MVP success definition

The MVP is successful if it can:

- ingest Polyvore items into a normalized schema
- retrieve candidate products per missing slot
- assemble complete outfit candidates from a seed item
- rerank complete outfits with an outfit-aware scorer
- produce short explanations for the top results
- evaluate offline on a held-out outfit dataset

---

## Notes for the team

This documentation assumes the following philosophy:

- **Prototype on Polyvore**
- **Abstract the item schema**
- **Swap in real client data later**
- **Keep the architecture modular so models can be replaced**

Do not hardcode logic around Polyvore-specific quirks in the core pipeline.
Instead, isolate dataset-specific logic in loaders and preprocessors.
