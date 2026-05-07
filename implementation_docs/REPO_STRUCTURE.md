# Repository Structure

## Suggested layout

```text
project-root/
├─ README.md
├─ PLANNING.md
├─ docs/
│  ├─ ARCHITECTURE.md
│  ├─ DATASETS_AND_SCHEMA.md
│  ├─ IMPLEMENTATION_GUIDE.md
│  ├─ METADATA_FALLBACK.md
│  ├─ EVALUATION.md
│  ├─ REPO_STRUCTURE.md
│  └─ TEAM_WORKFLOW.md
├─ configs/
│  ├─ base.yaml
│  ├─ retrieval.yaml
│  ├─ reranker.yaml
│  └─ api.yaml
├─ data/
│  ├─ raw/
│  ├─ normalized/
│  ├─ cache/
│  └─ eval/
├─ notebooks/
├─ scripts/
│  ├─ inspect_datasets.py
│  ├─ normalize_items.py
│  ├─ parse_metadata.py
│  ├─ build_embeddings.py
│  ├─ index_qdrant.py
│  ├─ retrieve_candidates.py
│  ├─ rerank_outfits.py
│  └─ run_eval.py
├─ src/
│  ├─ common/
│  ├─ config/
│  ├─ loaders/
│  ├─ normalization/
│  ├─ parsers/
│  ├─ embeddings/
│  ├─ vectorstore/
│  ├─ retrieval/
│  ├─ composition/
│  ├─ reranking/
│  ├─ explanation/
│  ├─ api/
│  └─ evaluation/
├─ tests/
└─ reports/
```

---

## Package responsibilities

### `loaders/`
Dataset- and source-specific readers.

### `normalization/`
Schema normalization and category-to-slot mapping.

### `parsers/`
Structured metadata parsing and fallback recovery.

### `embeddings/`
Dense embedding model wrappers.

### `vectorstore/`
Qdrant collection setup and search utilities.

### `retrieval/`
Slot-aware candidate generation.

### `composition/`
Outfit-template logic and learned composition hooks.

### `reranking/`
Compatibility scoring and ranking.

### `explanation/`
User-facing explanation generation.

### `evaluation/`
Offline metrics, benchmark tasks, and reporting.

---

## Coding guidelines

- keep each stage isolated
- use typed schemas
- preserve provenance
- keep configs external
- do not mix dataset-specific code into core modules
