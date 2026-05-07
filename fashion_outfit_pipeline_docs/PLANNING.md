# PLANNING.md

## Goal

Implement a modular outfit recommendation pipeline that can be tested end-to-end on Polyvore first, then adapted to real client product catalogs.

---

## Phase 0: Project setup

### Deliverables
- Git repository initialized
- Environment setup documented
- Dependency management chosen
- Directory structure created
- Qdrant local/dev instance running

### Tasks
- Choose Python version
- Choose package manager (`uv`, `poetry`, or `pip`)
- Create `.env.example`
- Add linting / formatting tools
- Define logging format
- Create initial config system

### Exit criteria
- Any team member can clone the repo and run the base project locally

---

## Phase 1: Data foundation

### Objective
Load and normalize test datasets into one internal schema.

### Deliverables
- Loader for `owj0421/polyvore`
- Loader for `owj0421/polyvore-outfits`
- Unified item schema
- Unified outfit schema
- Validation scripts
- Dataset statistics report

### Tasks
- Inspect item-level columns
- Inspect outfit-level columns
- Write schema mapping code
- Handle missing titles / descriptions
- Normalize categories into project slots
- Save normalized data to parquet/jsonl

### Exit criteria
- Normalized items and outfits can be loaded consistently
- Team understands what supervision is available

---

## Phase 2: Structured parsing and metadata normalization

### Objective
Guarantee minimum usable metadata for every item.

### Deliverables
- Metadata parser interface
- Qwen-based structured parsing module
- Confidence / source tracking for each field
- Fallback rules for missing metadata

### Tasks
- Define required and optional fields
- Create JSON schema for parsed metadata
- Implement Qwen prompting for metadata extraction
- Track field provenance:
  - source metadata
  - inferred from image
  - inferred from text
  - inferred from retrieval consensus
- Add repair / normalization rules

### Exit criteria
- Every indexed item has minimum required metadata

---

## Phase 3: Embedding and indexing

### Objective
Index the catalog in a way that supports fast filtered retrieval.

### Deliverables
- Embedding interface
- Dense embedding generation pipeline
- Qdrant collection with payload schema
- Indexing scripts
- Re-index support

### Tasks
- Implement embedding model wrapper
- Select text fields for embedding input
- Store dense vectors
- Store payload metadata
- Support filtering by slot/category and optional fields
- Build incremental indexing flow

### Exit criteria
- Items can be retrieved from Qdrant by vector similarity plus filters

---

## Phase 4: Retrieval

### Objective
Retrieve candidates for each missing outfit slot from a seed item.

### Deliverables
- Retrieval API
- Slot-aware candidate generator
- Filter configuration
- Retrieval diagnostics

### Tasks
- Define slot template logic
- Given a seed item, infer missing slots
- Retrieve top-k per missing slot
- Support keyword boosting and metadata filters
- Deduplicate candidates
- Log retrieval decisions

### Exit criteria
- Given a seed item, the system can return candidate pools by slot

---

## Phase 5: Outfit composition

### Objective
Assemble full candidate outfits from retrieved slot pools.

### Deliverables
- Composition interface
- Template-based composition baseline
- Optional learned composition model hook
- Candidate pruning logic

### Tasks
- Define allowed slot combinations
- Combine top-k candidates across slots
- Prune impossible or redundant combinations
- Preserve interpretable decision traces
- Add support for prompts / style constraints later

### Exit criteria
- The system can produce complete outfit candidates from one seed item

---

## Phase 6: Compatibility reranking

### Objective
Score full outfits, not just individual retrieved items.

### Deliverables
- Reranker interface
- Compatibility scorer
- Ranking pipeline
- Score breakdowns

### Tasks
- Define outfit-level scoring contract
- Integrate a compatibility model
- Add score components:
  - overall compatibility
  - style consistency
  - color harmony
  - season consistency
  - slot completeness
- Rank outfits by final score

### Exit criteria
- Final results are ranked by outfit-level quality

---

## Phase 7: Explanations and serving

### Objective
Produce user-facing outputs and wrap the system in an API.

### Deliverables
- Explanation generator
- FastAPI app
- Seed-item query endpoint
- Health and debug endpoints

### Tasks
- Build API response schema
- Generate concise explanations
- Expose ranked results
- Add debug mode to surface scores and filters
- Add latency and error logging

### Exit criteria
- A consumer can request outfit recommendations from an API

---

## Phase 8: Evaluation

### Objective
Prove the pipeline works offline before client deployment.

### Deliverables
- FITB evaluation pipeline
- Compatibility evaluation pipeline
- Retrieval analysis notebook/report
- Error taxonomy

### Tasks
- Evaluate candidate retrieval
- Evaluate reranker quality
- Measure slot accuracy where relevant
- Run qualitative review
- Categorize failure modes

### Exit criteria
- Team has a clear offline quality baseline

---

## Phase 9: Real-client data onboarding

### Objective
Adapt the tested architecture to production-style data.

### Deliverables
- Client data mapper
- Metadata fallback pipeline
- URL-based metadata recovery
- Validation checks

### Tasks
- Parse source feeds
- Recover missing fields from product pages if needed
- Normalize categories
- Validate image availability
- Backfill missing required fields

### Exit criteria
- Client feeds can be ingested without rewriting core recommendation logic

---

## Recommended owner split

### Person A: Data and schema
- loaders
- normalization
- dataset validation

### Person B: Retrieval and indexing
- embeddings
- Qdrant
- filtering
- retrieval logic

### Person C: Composition and reranking
- composition logic
- compatibility model
- scoring

### Person D: Serving and tooling
- API
- logging
- evaluation harness
- dashboards

---

## Risk list

### Risk 1: Missing metadata
Mitigation:
- metadata fallback flow
- field provenance tracking
- category normalization rules

### Risk 2: Weak retrieval quality
Mitigation:
- filtered retrieval
- better embedding model
- hybrid search
- slot-aware search

### Risk 3: Expensive scoring
Mitigation:
- cheap pruning before reranking
- score only top candidate outfits
- cache parse and explanation outputs

### Risk 4: Dataset mismatch to client catalogs
Mitigation:
- abstract schema
- keep dataset-specific code isolated
- test metadata fallback early

---

## Minimum viable milestone sequence

If time is tight, implement in this order:

1. dataset loading
2. schema normalization
3. embedding + Qdrant indexing
4. slot-aware retrieval
5. template-based composition
6. compatibility reranking
7. API
8. explanation generation
