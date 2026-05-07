# Datasets and Schema

## Datasets used for offline development

### 1. Item catalog dataset
Use `owj0421/polyvore` as the searchable catalog.

Expected use:
- item-level indexing
- metadata experiments
- embedding generation
- retrieval tests

### 2. Outfit supervision dataset
Use `owj0421/polyvore-outfits` for:
- compatibility evaluation
- fill-in-the-blank evaluation
- reranker development
- composition validation

---

## Why use both datasets

The item dataset gives you the searchable inventory.
The outfit dataset gives you the ground truth relationships between items.

Together, they let you test:
- can you retrieve plausible candidates?
- can you assemble them into outfits?
- can you rank good outfits above bad ones?

---

## Minimum internal item schema

Every item should be normalized to this structure:

```json
{
  "item_id": "string",
  "image": "path-or-url",
  "title": "string-or-empty",
  "description": "string-or-empty",
  "raw_category": "string-or-empty",
  "slot": "one-of-fixed-slot-set",
  "subcategory": "string-or-empty",
  "department": "string-or-empty",
  "price": "number-or-null",
  "currency": "string-or-null",
  "stock_status": "string-or-empty",
  "attributes": {
    "color": [],
    "material": [],
    "pattern": [],
    "season": [],
    "occasion": []
  },
  "field_sources": {},
  "embedding_status": "pending|done|failed"
}
```

---

## Recommended slot set

Use a controlled slot vocabulary:

- `top`
- `bottom`
- `outerwear`
- `shoes`
- `accessory`
- `dress_or_all_body`

This is intentionally smaller than raw merchant categories.

---

## Example category mapping

Map dataset or client categories into the slot set.

### Possible mapping examples
- tops -> top
- bottoms -> bottom
- outerwear -> outerwear
- shoes -> shoes
- bags -> accessory
- jewellery -> accessory
- hats -> accessory
- scarves -> accessory
- sunglasses -> accessory
- dresses / all-body -> dress_or_all_body

Keep the original category as `raw_category`.
Do not discard it.

---

## Outfit schema

Use a consistent structure for candidate outfits and ground-truth outfits.

```json
{
  "outfit_id": "string",
  "seed_item_id": "string",
  "items": {
    "top": "item_id-or-null",
    "bottom": "item_id-or-null",
    "outerwear": "item_id-or-null",
    "shoes": "item_id-or-null",
    "accessory": ["item_id", "item_id"]
  },
  "source": "ground_truth|generated",
  "scores": {
    "retrieval": 0.0,
    "compatibility": 0.0,
    "final": 0.0
  }
}
```

---

## Field provenance

For every inferred or normalized field, keep provenance.

Recommended values:
- `client_metadata`
- `dataset_metadata`
- `url_structured_data`
- `open_graph`
- `vlm_inference`
- `text_inference`
- `retrieval_consensus`
- `manual_override`

This matters when debugging unexpected outputs.

---

## What can be missing

Expect these fields to be missing sometimes:
- title
- description
- department
- price
- stock_status
- material
- occasion

The system should still work with:
- image
- slot/category
- a short text field if available

---

## Data validation checklist

Before indexing, validate:

- `item_id` exists
- image is reachable or stored locally
- slot is mapped into controlled vocabulary
- title and description are strings, even if empty
- text fields are normalized to unicode-safe strings
- duplicate items are handled
- embedding job status is tracked

---

## Dataset-specific caution

Polyvore is useful for offline development, but it is not the same as real retailer data.

Common differences you should expect later:
- retailer taxonomies may be messy or overly granular
- stock and pricing fields may matter in production
- client images may have different styles and backgrounds
- titles may be shorter or noisier
- some catalogs may include bundles or non-apparel items

Therefore:
- isolate dataset loaders
- keep the internal schema generic
- do not let Polyvore-specific assumptions leak into the core pipeline
