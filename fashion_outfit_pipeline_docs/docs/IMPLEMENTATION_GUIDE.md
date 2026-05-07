# Implementation Guide

## Step 1: Set up the project skeleton

Create:
- config module
- dataset loaders
- model wrappers
- retrieval package
- reranking package
- api package
- evaluation package

Use the repo structure in `REPO_STRUCTURE.md`.

---

## Step 2: Load and inspect Polyvore data

Tasks:
- load the item dataset
- load the outfit dataset
- print sample rows
- compute missing-value counts
- list category values
- identify any category normalization issues

Outputs:
- `data/normalized/items.parquet`
- `data/normalized/outfits.parquet`
- `reports/dataset_profile.md`

---

## Step 3: Normalize item metadata

Build a normalizer that:
- standardizes field names
- maps category to slot
- cleans empty text fields
- records provenance
- stores unresolved missing fields

At this stage, do not try to be perfect.
Just produce a stable item schema.

---

## Step 4: Add structured parsing

Build a parser interface:
- input: normalized item
- output: enriched normalized item

Start with a Qwen prompt that extracts:
- slot
- subcategory
- colors
- material
- pattern
- season
- occasion

Use it selectively:
- when the field is missing
- when the raw category is too broad
- when the title is weak

Do not run it for every item if source metadata is already reliable.

---

## Step 5: Build embeddings

Create an embedding service wrapper.

Input fields:
- image
- title
- slot
- short description

Store:
- embedding vector
- model name
- embedding timestamp
- input hash

Tip:
Keep embedding generation batch-friendly and resumable.

---

## Step 6: Stand up Qdrant

Create a Qdrant collection with:
- vector field
- payload fields for filtering

Payload fields should include at least:
- item_id
- slot
- raw_category
- department
- price
- stock_status
- color tokens
- season tokens

Index all normalized items.

---

## Step 7: Build seed-item retrieval

Input:
- a seed item id or seed item object

Process:
1. identify seed slot
2. choose a slot template
3. retrieve candidates per missing slot
4. apply hard filters
5. deduplicate results

Output:
- candidate pools by slot

Start with simple templates.

Example:
- seed top -> {bottom, shoes, outerwear? accessory?}
- seed dress -> {shoes, outerwear?, accessory?}

---

## Step 8: Assemble outfit candidates

Build combinations from the per-slot pools.

Start simple:
- top-k bottom candidates
- top-k shoes candidates
- optional outerwear/accessory

Then prune:
- duplicate item reuse
- obvious slot conflicts
- overly repetitive outfits

Keep the candidate count manageable before reranking.

---

## Step 9: Add compatibility reranking

Create a reranker interface:
- input: list of candidate outfits
- output: same list with compatibility scores

Required outputs:
- overall score
- breakdown by component
- reason codes if available

Make sure the reranker sees the whole outfit context.

---

## Step 10: Add explanation generation

Use the top final outfits and produce:
- one short summary
- optional style tags
- optional confidence note

Do not let the explanation invent constraints that were never checked.

---

## Step 11: Build the API

Recommended request:
```json
{
  "seed_item_id": "123",
  "constraints": {
    "budget_max": null,
    "season": null,
    "occasion": null
  },
  "debug": false
}
```

Recommended response:
```json
{
  "seed_item_id": "123",
  "results": [
    {
      "items": {...},
      "scores": {...},
      "explanation": "..."
    }
  ]
}
```

---

## Step 12: Evaluate

Run:
- retrieval quality checks
- fill-in-the-blank evaluation
- compatibility ranking evaluation
- qualitative review

Log failure classes:
- wrong slot
- weak style match
- repetitive recommendations
- missing metadata harm
- reranker disagreement with human judgment

---

## Practical implementation rules

### Rule 1
Never let missing optional metadata crash the pipeline.

### Rule 2
Do not tightly couple parsing, retrieval, and ranking code.

### Rule 3
Every major stage should have:
- input schema
- output schema
- logging
- unit tests

### Rule 4
Cache per-item computations aggressively.

### Rule 5
Always preserve raw source fields alongside normalized fields.

---

## Suggested first working baseline

Build this before anything fancy:

1. normalize Polyvore items
2. map category to slot
3. create dense embeddings
4. retrieve top-k per missing slot
5. assemble simple outfits
6. rerank with a compatibility scorer
7. return top 3 outfits

Only after that:
- add better metadata parsing
- add better explanations
- add more constraints
- add client-specific adapters
