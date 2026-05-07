# Team Workflow

## Working style

Treat the system as a pipeline of contracts.

Each team member should own one or more modules with:
- clear inputs
- clear outputs
- test coverage
- logging

Avoid hidden coupling.

---

## Recommended ownership

### Data owner
Responsible for:
- dataset loaders
- normalization
- schema validation
- dataset reports

### Retrieval owner
Responsible for:
- embeddings
- Qdrant
- filters
- candidate generation

### Ranking owner
Responsible for:
- composition logic
- reranking model
- score fusion

### Product/API owner
Responsible for:
- serving
- explanation layer
- developer tooling
- debug endpoints

---

## Weekly workflow

### Early week
- define goals and interface changes
- assign ownership
- freeze shared schema changes

### Mid week
- implement module work
- merge behind feature flags if needed
- run component-level tests

### End of week
- run end-to-end evaluation
- review sample outputs
- log failure modes
- update docs and configs

---

## Interface-first development

For each module, define:

### Input schema
What exact fields come in?

### Output schema
What exact fields come out?

### Error modes
What can fail, and how is it reported?

### Config knobs
What can be tuned externally?

This prevents pipeline breakage when multiple people work in parallel.

---

## Change policy

When changing:
- normalized item schema
- slot vocabulary
- reranker output schema
- API response schema

also update:
- docs
- configs
- tests
- sample fixtures

---

## Review checklist

Before merging:
- does the module preserve provenance?
- does it fail safely on missing fields?
- are logs useful?
- are configs externalized?
- is there at least one integration test?
- is the README/docs still accurate?

---

## Communication note

Keep a shared failure log.
Do not only track successes.

Example failure tags:
- metadata_missing
- slot_wrong
- retrieval_noise
- reranker_disagreement
- duplicate_outfits
- explanation_mismatch

These labels will be more useful than vague notes later.
