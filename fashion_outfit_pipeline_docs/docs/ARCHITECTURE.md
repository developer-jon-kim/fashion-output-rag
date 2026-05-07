# Architecture

## System overview

This system recommends complete outfits from a seed product.

It is designed as a modular pipeline:

1. **Input normalization**
2. **Structured metadata parsing**
3. **Embedding generation**
4. **Hybrid retrieval**
5. **Outfit composition**
6. **Compatibility reranking**
7. **Explanation generation**
8. **API delivery**

---

## Why modularity matters

Different tasks in this problem are different model problems:

- parsing metadata is a structured multimodal understanding problem
- retrieval is a dense / hybrid search problem
- outfit completion is a composition problem
- ranking complete outfits is a compatibility problem
- explanations are a generation problem

Do not force one model to do all of them.

---

## Core modules

## 1. Input normalization

### Purpose
Convert raw data from any source into one internal item schema.

### Inputs
- Polyvore records
- client CSV/JSON feed
- product page URLs
- image files

### Outputs
A normalized item object.

### Example normalized item
```json
{
  "item_id": "12345",
  "image_url": "https://...",
  "title": "Navy wool overcoat",
  "description": "Long single-breasted coat...",
  "raw_category": "Coats",
  "slot": "outerwear",
  "department": "women",
  "price": 249.99,
  "currency": "USD",
  "stock_status": "in_stock"
}
```

---

## 2. Structured metadata parsing

### Purpose
Fill gaps and normalize inconsistent fields.

### Suggested model role
Qwen2.5-VL parses image + text into structured JSON.

### Outputs
- slot
- subcategory
- color
- material
- pattern
- silhouette
- formality
- season
- occasion
- confidence
- provenance

### Key requirement
Every field should store both value and source.

Example:
```json
{
  "slot": {"value": "shoes", "source": "client_metadata"},
  "material": {"value": "leather", "source": "vlm_inference"},
  "season": {"value": "fall", "source": "vlm_inference"}
}
```

---

## 3. Embedding generation

### Purpose
Produce vectors for dense retrieval.

### Suggested models
- Fashion SigLIP 2
- GR-Lite
- Marqo FashionSigLIP

### Inputs
- product image
- selected text fields

### Recommended text fields
- title
- category / slot
- description
- optional color/material tokens

### Output
- dense embedding vector

---

## 4. Hybrid retrieval

### Purpose
Find strong candidates for each missing outfit slot.

### Engine
Qdrant

### Retrieval strategy
Use:
- dense fashion embedding search
- optional sparse/keyword search
- payload filters

### Typical filters
- slot
- department
- stock status
- price range
- retailer
- season

### Important principle
Retrieve **per slot**, not across the whole catalog at once.

---

## 5. Outfit composition

### Purpose
Turn a seed item and candidate pools into complete outfit candidates.

### Baseline approach
Template-based composition:
- seed top -> retrieve bottom + shoes + optional outerwear/accessory
- seed bottom -> retrieve top + shoes + optional outerwear/accessory
- seed outerwear -> retrieve top + bottom + shoes

### Advanced approach
Use a learned composition model to infer the best structure.

### Output
A list of candidate outfits, each with:
- items by slot
- composition trace
- pre-rerank score

---

## 6. Compatibility reranking

### Purpose
Judge complete outfits holistically.

### Suggested models
- MEDAL
- OutfitTransformer
- VICTOR

### Score dimensions
- overall compatibility
- color harmony
- style coherence
- seasonal consistency
- occasion consistency
- completeness
- penalty terms

### Output
A ranked list of outfits with score breakdown.

---

## 7. Explanation generation

### Purpose
Produce short explanations for the final top outfits.

### Suggested model role
Qwen2.5-VL

### Example output
```json
{
  "summary": "This outfit works because the neutral trousers balance the statement outerwear, while the shoes keep the formality consistent.",
  "tags": ["smart casual", "fall", "neutral palette"]
}
```

### Constraint
Explanations should be short, factual, and tied to visible attributes.

---

## 8. API delivery

### Suggested endpoints
- `POST /parse-item`
- `POST /index-item`
- `POST /recommend-outfits`
- `POST /evaluate-fitb`
- `GET /health`

### Debug mode response
Include:
- selected slot template
- retrieval filters
- candidate pools
- reranker score breakdown
- explanation prompt/result

---

## Data flow

```text
Raw item
 -> normalization
 -> structured parsing
 -> embedding generation
 -> Qdrant indexing

Seed item query
 -> normalized seed item
 -> parse / repair if needed
 -> infer missing slots
 -> retrieve candidates per slot
 -> assemble outfits
 -> rerank
 -> explain
 -> return response
```

---

## Caching strategy

Cache:
- parsed metadata
- embeddings
- candidate pools for repeated seed items
- explanation outputs for top results

Do not recompute stable per-item features at request time if you can precompute them.

---

## Observability

Track:
- parse failures
- missing metadata rates
- embedding generation failures
- retrieval latency
- candidate pool sizes
- reranker latency
- explanation latency
- end-to-end latency

Also log failure categories:
- wrong slot retrieval
- weak outfit coherence
- duplicate results
- incomplete outfit
- explanation mismatch
