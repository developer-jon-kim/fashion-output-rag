# Step-by-Step Coding Guide for Each Approach

This file turns the four architecture approaches into concrete coding steps.

Use it after reading:
- `README.md`
- `PLANNING.md`
- `docs/REPO_STRUCTURE.md`
- `docs/DATASETS_AND_SCHEMA.md`

The recommended way to implement all approaches is:
1. build the shared foundation once
2. implement Approach 3 or 2 first as a baseline
3. add Approach 4 if prompt control matters
4. add Approach 1 last if you can access the strongest models

---

## 0. Shared foundation for all approaches

Build these modules once before implementing any specific approach.

### 0.1 Create the repo skeleton

Create these folders:

```text
src/
  config/
  data/
  parsers/
  embedders/
  retrievers/
  composers/
  rerankers/
  explainers/
  evaluation/
  api/
  utils/
notebooks/
scripts/
tests/
```

### 0.2 Define the core schemas

Create a shared item schema:

```python
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any

@dataclass
class NormalizedItem:
    item_id: str
    image_path_or_url: str
    title: Optional[str] = None
    description: Optional[str] = None
    raw_category: Optional[str] = None
    slot: Optional[str] = None
    subcategory: Optional[str] = None
    department: Optional[str] = None
    colors: List[str] = field(default_factory=list)
    material: Optional[str] = None
    pattern: Optional[str] = None
    season: Optional[str] = None
    occasion: Optional[str] = None
    brand: Optional[str] = None
    price: Optional[float] = None
    currency: Optional[str] = None
    stock_status: Optional[str] = None
    metadata_source: Dict[str, str] = field(default_factory=dict)
    extra: Dict[str, Any] = field(default_factory=dict)
```

Create an outfit candidate schema:

```python
@dataclass
class OutfitCandidate:
    seed_item_id: str
    item_ids: List[str]
    slot_map: Dict[str, str]
    retrieval_scores: Dict[str, float] = field(default_factory=dict)
    rerank_score: Optional[float] = None
    explanation: Optional[str] = None
    extra: Dict[str, Any] = field(default_factory=dict)
```

### 0.3 Create the shared interfaces

Define one interface per swappable module:

```python
class MetadataParser:
    def parse(self, item: NormalizedItem) -> NormalizedItem:
        raise NotImplementedError

class Embedder:
    def embed_item(self, item: NormalizedItem):
        raise NotImplementedError

class Retriever:
    def search(self, query_item: NormalizedItem, target_slot: str, top_k: int = 20):
        raise NotImplementedError

class Composer:
    def compose(self, seed_item: NormalizedItem, retrieved_by_slot: dict, constraints: dict | None = None):
        raise NotImplementedError

class Reranker:
    def score(self, outfits: list[OutfitCandidate], context: dict | None = None):
        raise NotImplementedError

class Explainer:
    def explain(self, outfit: OutfitCandidate, context: dict | None = None) -> str:
        raise NotImplementedError
```

### 0.4 Build dataset loaders

Create:
- `src/data/load_polyvore_items.py`
- `src/data/load_polyvore_outfits.py`
- `src/data/normalize_polyvore.py`

Tasks:
1. load the Polyvore item dataset
2. map `category` to internal `slot`
3. keep `title`, `description`, and `image`
4. create train/validation/test splits for experiments
5. store normalized outputs as parquet or jsonl

### 0.5 Add metadata fallback utilities

Implement utility functions for:
- title cleanup
- category-to-slot mapping
- empty field detection
- inferred-field provenance tracking

### 0.6 Stand up Qdrant

Implement:
- collection creation
- payload schema setup
- upsert helper
- filtered search helper

At minimum, store payload fields for:
- `item_id`
- `slot`
- `subcategory`
- `department`
- `season`
- `brand`
- `price`
- `stock_status`

### 0.7 Build the first evaluation harness

Create offline metrics for:
- retrieval precision by slot
- top-k hit rate
- compatibility ranking quality
- fill-in-the-blank style retrieval accuracy

Once the shared foundation works, move to a specific approach.

---

## 1. Approach 1 — Highest-ceiling / best projected outcome

Reference: `docs/APPROACH_1_HIGHEST_CEILING.md`

### Goal

Use the strongest specialized model at each stage.

### Stack

- Parser: Qwen2.5-VL
- Embedder: Fashion SigLIP 2
- Retriever store: Qdrant
- Composer: Text2Outfit
- Reranker: MEDAL
- Explainer: Qwen2.5-VL

### Step-by-step coding order

#### Step 1: Implement the Qwen parser wrapper

Create `src/parsers/qwen_vl_parser.py`.

It should:
1. take `image + title + description + raw_category`
2. ask Qwen for structured JSON
3. fill missing fields only
4. preserve original source metadata when available

Expected output fields:
- `slot`
- `subcategory`
- `colors`
- `material`
- `pattern`
- `season`
- `occasion`
- `department`
- `canonical_title`

#### Step 2: Implement the Fashion SigLIP 2 embedder wrapper

Create `src/embedders/fashion_siglip2.py`.

It should:
1. build the model input from image + compact text
2. generate one dense vector per item
3. expose `embed_item()` and `embed_query()`

Suggested text input:

```text
{title}. category: {slot}. subcategory: {subcategory}. description: {description}
```

#### Step 3: Implement Qdrant indexing for Approach 1

Create `src/retrievers/qdrant_retriever.py`.

Tasks:
1. create the collection
2. insert embedding vectors
3. attach payload metadata
4. support filtered retrieval by target slot
5. optionally combine dense search with sparse/title search

#### Step 4: Implement the Text2Outfit composer wrapper

Create `src/composers/text2outfit_composer.py`.

It should:
1. accept the seed item
2. infer which slots need filling
3. optionally accept user constraints
4. produce one or more composition plans

Output example:

```python
{
    "required_slots": ["bottom", "shoes"],
    "optional_slots": ["outerwear", "accessory"],
    "style_constraints": {"season": "fall", "occasion": "smart casual"}
}
```

#### Step 5: Implement outfit assembly

Create `src/composers/outfit_assembler.py`.

Tasks:
1. retrieve top-k items for each required slot
2. combine them into candidate outfits
3. optionally add optional slots
4. deduplicate near-identical candidates
5. cap the number of outfits before reranking

#### Step 6: Implement MEDAL reranking

Create `src/rerankers/medal_reranker.py`.

It should:
1. accept full outfit candidates
2. return a numeric compatibility score
3. sort outfits by score descending
4. optionally return per-pair or per-item signals if available

#### Step 7: Implement Qwen explanation generation

Create `src/explainers/qwen_explainer.py`.

It should:
1. take only the final top outfits
2. generate short explanations
3. mention style compatibility, color harmony, and occasion alignment

#### Step 8: Create a complete pipeline runner

Create `scripts/run_approach_1.py`.

Pipeline order:
1. load normalized item
2. parse with Qwen if needed
3. embed and index catalog
4. compose slots with Text2Outfit
5. retrieve per slot
6. assemble outfits
7. rerank with MEDAL
8. explain with Qwen
9. write outputs to json

#### Step 9: Add tests

Create tests for:
- parser JSON format
- embedder output shape
- Qdrant filtered retrieval
- composer slot plan generation
- reranker returns sorted scores

---

## 2. Approach 2 — Best fully open

Reference: `docs/APPROACH_2_FULLY_OPEN.md`

### Goal

Use accessible models without depending on closed or hard-to-access components.

### Stack

- Parser: Qwen2.5-VL
- Embedder: GR-Lite or Marqo FashionSigLIP
- Retriever store: Qdrant
- Composer: template-based composition
- Reranker: OutfitTransformer or VICTOR
- Explainer: Qwen2.5-VL

### Step-by-step coding order

#### Step 1: Implement the open embedder wrapper

Create either:
- `src/embedders/gr_lite.py`
- `src/embedders/marqo_fashion_siglip.py`

The wrapper should:
1. expose a unified `embed_item()` API
2. normalize the text input format
3. return vectors compatible with Qdrant

#### Step 2: Implement template-based composition

Create `src/composers/template_composer.py`.

Start with deterministic templates:

```python
TEMPLATES = {
    "top": ["bottom", "shoes"],
    "dress": ["shoes"],
    "outerwear": ["top", "bottom", "shoes"],
    "bottom": ["top", "shoes"],
    "shoes": ["top", "bottom"],
}
```

Tasks:
1. map seed slot to required and optional slots
2. allow simple override rules
3. keep outputs deterministic

#### Step 3: Implement filtered retrieval

Reuse `qdrant_retriever.py` and add:
1. slot filter
2. exclude the seed item
3. optional diversity filter
4. optional lexical boost from title/description

#### Step 4: Implement the outfit assembler

Reuse or extend `src/composers/outfit_assembler.py`.

Keep assembly simple:
1. choose top candidates per slot
2. generate a manageable number of combinations
3. record retrieval scores per item

#### Step 5: Implement the reranker

Choose one:
- `src/rerankers/outfit_transformer.py`
- `src/rerankers/victor_reranker.py`

Tasks:
1. define the input representation for a full outfit
2. load the pretrained or finetuned model
3. score each candidate outfit
4. sort the results

#### Step 6: Implement explanation generation

Reuse `src/explainers/qwen_explainer.py`.

#### Step 7: Create a complete pipeline runner

Create `scripts/run_approach_2.py`.

Pipeline order:
1. load seed item
2. run metadata recovery only if needed
3. get target slots from the template composer
4. retrieve candidates by slot
5. assemble outfits
6. rerank with OutfitTransformer or VICTOR
7. explain with Qwen

#### Step 8: Add tests

Focus on:
- template slot mapping
- retrieval correctness by slot
- reranker output ordering
- end-to-end pipeline sanity checks

---

## 3. Approach 3 — Best production-first

Reference: `docs/APPROACH_3_PRODUCTION_FIRST.md`

### Goal

Prefer reliability and easier deployment to real client catalogs.

### Stack

- Parser: source taxonomy first, Qwen fallback
- Embedder: Marqo FashionSigLIP or OpenFashionCLIP
- Retriever store: Qdrant
- Composer: template-based composition
- Reranker: MEDAL
- Explainer: Qwen2.5-VL

### Step-by-step coding order

#### Step 1: Implement taxonomy mapping

Create `src/parsers/taxonomy_mapper.py`.

Tasks:
1. map source categories to internal slots
2. preserve the raw source category
3. track confidence and provenance

Example:

```python
SOURCE_TO_SLOT = {
    "tops": "top",
    "bottoms": "bottom",
    "outerwear": "outerwear",
    "shoes": "shoes",
    "bags": "accessory",
    "jewellery": "accessory",
}
```

#### Step 2: Implement metadata provenance tracking

Create `src/utils/provenance.py`.

Track whether each field came from:
- source metadata
- product-page parsing
- text inference
- Qwen inference
- retrieval consensus

This matters for debugging and production trust.

#### Step 3: Implement conservative Qwen fallback parsing

Create `src/parsers/qwen_fallback_parser.py`.

Rules:
1. only call Qwen when a required field is missing
2. do not overwrite trusted source fields unless explicitly allowed
3. mark inferred fields clearly

#### Step 4: Implement the production retriever wrapper

Create either:
- `src/embedders/marqo_fashion_siglip.py`
- `src/embedders/openfashionclip.py`

Then enforce stronger Qdrant payload filtering.

At minimum, filter by:
- slot
- department if available
- stock status if available
- season if available
- price band if available

#### Step 5: Implement template-based composition

Reuse `src/composers/template_composer.py`.

Keep this simple and stable.

#### Step 6: Implement MEDAL reranking

Reuse `src/rerankers/medal_reranker.py`.

#### Step 7: Implement explanation generation

Reuse `src/explainers/qwen_explainer.py`.

#### Step 8: Create a complete pipeline runner

Create `scripts/run_approach_3.py`.

Pipeline order:
1. normalize source metadata
2. map taxonomy to internal slots
3. fill missing fields conservatively
4. embed and index items
5. retrieve using strict filters
6. assemble template-based outfits
7. rerank with MEDAL
8. explain top results

#### Step 9: Add tests

Focus on:
- taxonomy mapping correctness
- provenance tracking
- strict filter behavior
- behavior when fields are missing

---

## 4. Approach 4 — Best prompt-controllable

Reference: `docs/APPROACH_4_PROMPT_CONTROLLABLE.md`

### Goal

Support user- or client-provided natural language constraints.

### Stack

- Parser/controller: Qwen2.5-VL
- Embedder: FashionSigLIP or GR-Lite
- Retriever store: Qdrant
- Composer: Text2Outfit
- Reranker: MEDAL or VICTOR
- Explainer: Qwen2.5-VL

### Step-by-step coding order

#### Step 1: Define the prompt constraint schema

Create `src/parsers/constraint_schema.py`.

Example:

```python
from dataclasses import dataclass, field

@dataclass
class PromptConstraints:
    occasion: str | None = None
    season: str | None = None
    color_preferences: list[str] = field(default_factory=list)
    style_keywords: list[str] = field(default_factory=list)
    budget_preference: str | None = None
    required_slots: list[str] = field(default_factory=list)
    forbidden_slots: list[str] = field(default_factory=list)
```

#### Step 2: Implement the Qwen prompt parser

Create `src/parsers/qwen_prompt_parser.py`.

Tasks:
1. take a seed item and user prompt
2. convert free text into structured constraints
3. validate the JSON output
4. return a `PromptConstraints` object

#### Step 3: Implement the retriever wrapper

Create or reuse:
- `src/embedders/gr_lite.py`
- `src/embedders/marqo_fashion_siglip.py`

Then extend the retriever so it can use prompt-derived filters or boosts.

Examples:
- boost black items for monochrome prompts
- filter to fall items for season constraints
- exclude accessories if forbidden

#### Step 4: Implement Text2Outfit composition with constraints

Create `src/composers/text2outfit_constrained.py`.

Tasks:
1. accept the seed item + parsed constraints
2. output required and optional slots
3. pass style constraints into composition

#### Step 5: Implement outfit assembly under constraints

Extend `src/composers/outfit_assembler.py`.

Tasks:
1. remove candidates violating forbidden constraints
2. favor candidates matching requested style keywords
3. keep candidate counts manageable

#### Step 6: Implement the reranker

Choose one:
- `src/rerankers/medal_reranker.py`
- `src/rerankers/victor_reranker.py`

Make sure it can receive the prompt context as additional metadata if useful.

#### Step 7: Implement explanation generation

Reuse `src/explainers/qwen_explainer.py`, but pass the prompt constraints so the explanation can mention them.

#### Step 8: Create a complete pipeline runner

Create `scripts/run_approach_4.py`.

Pipeline order:
1. load seed item
2. parse the prompt into constraints
3. retrieve slot-aware candidates with constraint-aware filtering
4. compose with Text2Outfit
5. assemble outfits
6. rerank with MEDAL or VICTOR
7. generate a prompt-aware explanation

#### Step 9: Add tests

Focus on:
- prompt-to-JSON parsing
- constraint validation
- retrieval behavior under constraints
- forbidden-slot enforcement

---

## 5. Suggested order if you want to code all approaches

If your goal is to implement every approach efficiently, do this:

### Stage A — Common baseline
1. shared schemas
2. Polyvore loaders
3. Qdrant indexing
4. one embedder
5. one template composer
6. one reranker
7. one explainer

### Stage B — Easiest useful full system
Implement **Approach 3** or **Approach 2** first.

Reason:
- less dependency risk
- easier to debug
- strong enough to validate the full pipeline

### Stage C — Prompt-control variant
Add **Approach 4** next.

Reason:
- it mostly reuses the same retrieval and reranking base
- the main new work is prompt parsing and constraint-aware composition

### Stage D — Highest-ceiling variant
Add **Approach 1** last.

Reason:
- strongest but most complex
- depends on highest-end composition and reranking stack
- easiest to layer on once the shared core already works

---

## 6. What should stay identical across all approaches

Keep these pieces stable across approaches:
- normalized item schema
- outfit candidate schema
- Qdrant payload shape
- logging format
- evaluation harness
- output contract for API responses

That way, switching approaches is mostly swapping:
- parser
- embedder
- composer
- reranker

instead of rewriting the entire system.

---

## 7. Final advice

If you are coding this alone or with a small team:
- implement **Approach 3 first** if you care most about real deployment later
- implement **Approach 2 first** if you want the cleanest open baseline
- implement **Approach 4** once the base pipeline works
- implement **Approach 1** only after the common interfaces are stable

