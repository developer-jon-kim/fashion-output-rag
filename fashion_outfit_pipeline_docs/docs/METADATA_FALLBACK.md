# Metadata Fallback

## Why this exists

Real client catalogs are often incomplete.

The recommendation pipeline should not depend on perfect metadata.
Instead, it should recover a **minimum usable metadata set** automatically.

---

## Minimum usable metadata

The minimum fields to make the pipeline work well are:

- `item_id`
- `image`
- `title` or short text
- `slot/category`

Helpful but not strictly required:
- `description`
- `department`
- `price`
- `stock_status`
- `material`
- `color`

---

## Fallback order

When metadata is missing, recover it in this order:

### 1. Source metadata
Use whatever the client or dataset already provides.

### 2. Product-page structured data
If a product URL exists, parse:
- JSON-LD
- Schema.org Product fields
- Open Graph tags
- page title
- canonical URL

### 3. Text inference
Use title, breadcrumbs, description, and URL slug to infer:
- slot
- subcategory
- department
- style hints

### 4. VLM inference
Use Qwen2.5-VL to infer:
- slot
- subcategory
- color
- material
- pattern
- season
- occasion

### 5. Retrieval consensus
If a field is still uncertain, inspect nearest neighbors and infer from majority agreement.

---

## Slot recovery strategies

## Best case
Client already provides category -> map to slot.

## Good case
Use title/description keywords.

Examples:
- blazer -> outerwear
- loafers -> shoes
- trousers -> bottom
- tote bag -> accessory

## Fallback case
Use VLM image understanding.

## Last resort
Use retrieval-neighbor consensus.

---

## Title recovery strategies

## Best case
Use original title from metadata or product page.

## Good case
Normalize a noisy title.

Example:
- `WMN LTHR BT BLK`
- becomes
- `Women's black leather boots`

## Fallback case
Generate a canonical title from extracted attributes:
- color
- material
- subcategory

Example:
- `Black leather ankle boots`

---

## Department recovery

Potential sources:
- explicit metadata
- breadcrumbs
- description text
- URL path
- nearest-neighbor consensus

Example heuristic:
If title/description contains no signal, and the nearest 20 visually similar neighbors are mostly in one department, assign that department with low confidence.

---

## Price and stock recovery

These are usually not inferable from image alone.

Recover from:
- client feed
- product-page structured data
- HTML page parsing
- commerce API if available

If unavailable:
- keep as null
- do not fabricate values

---

## Confidence and provenance

Every recovered field should track:
- `value`
- `confidence`
- `source`

Example:
```json
{
  "slot": {
    "value": "outerwear",
    "confidence": 0.92,
    "source": "text_inference"
  }
}
```

---

## Operational policy

### Safe to infer
- slot
- subcategory
- color
- material
- pattern
- season
- occasion
- canonical title

### Unsafe to hallucinate
- price
- stock status
- retailer
- SKU
- exact fabric composition
- exact sizing availability

If a field is unsafe to infer, leave it missing.

---

## Decision policy

Use inferred fields for:
- retrieval filters
- ranking hints
- explanations

Do not use low-confidence inferred business fields to:
- block products
- create hard pricing constraints
- claim factual availability

---

## Polyvore testing note

Polyvore is a good place to simulate missing metadata.

Suggested tests:
- remove title
- remove description
- remove category
- keep image only
- compare pipeline quality before and after fallback recovery

This will help estimate how robust the metadata recovery path is before real client deployment.
