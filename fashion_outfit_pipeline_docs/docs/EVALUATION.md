# Evaluation

## Why evaluate offline first

Before real client deployment, the team should prove that the system works on offline fashion benchmarks.

Use:
- `owj0421/polyvore` for item retrieval experiments
- `owj0421/polyvore-outfits` for outfit-level evaluation

---

## Evaluation layers

### 1. Parsing quality
Questions:
- did slot recovery work?
- are titles reasonable?
- are extracted attributes plausible?

Metrics:
- slot accuracy on known fields
- manual review of inferred titles
- missing-field recovery rate

### 2. Retrieval quality
Questions:
- do candidate pools contain plausible items?
- are the candidates in the correct slot?
- are they visually / semantically relevant?

Metrics:
- Recall@K
- MRR
- nDCG
- slot purity
- human review on sampled queries

### 3. Outfit composition quality
Questions:
- are the generated outfits structurally complete?
- are slot templates sensible?

Metrics:
- completeness rate
- duplicate rate
- invalid combination rate

### 4. Compatibility reranking quality
Questions:
- does the reranker put good outfits above weak ones?

Metrics:
- AUC for compatibility classification
- ranking correlation
- Recall@K
- FITB accuracy

### 5. End-to-end recommendation quality
Questions:
- given a seed item, are the final top results acceptable?

Metrics:
- top-1 acceptance in human review
- top-3 acceptance
- diversity across top results
- explanation usefulness

---

## Recommended benchmark tasks

## Task A: Fill-in-the-blank
Given a partial outfit and multiple candidate items, choose the correct missing item.

Why it matters:
This directly measures complementary retrieval.

## Task B: Compatibility prediction
Given a full outfit, classify or rank whether it is compatible.

Why it matters:
This measures outfit-level reasoning.

## Task C: Seed-to-outfit generation
Given a single seed item, generate full outfits and evaluate with:
- reranker score
- human review
- optional proxy metrics against held-out outfits

---

## Failure taxonomy

Track at least these failure classes:

- wrong slot retrieval
- visually similar but stylistically incompatible
- incompatible formality
- season mismatch
- too many repetitive recommendations
- missing metadata damage
- overconfident explanation
- weak accessory selection

A good error taxonomy will make iteration much faster.

---

## Human review rubric

For sampled outputs, ask reviewers to rate:

1. slot correctness
2. visual compatibility
3. style coherence
4. season coherence
5. whether they would actually wear / show the outfit
6. whether the explanation matches the outfit

Use a 1 to 5 scale and preserve reviewer notes.

---

## Minimum reporting bundle

Every evaluation run should output:

- model versions
- dataset version
- config snapshot
- retrieval metrics
- reranker metrics
- sample qualitative outputs
- failure breakdown
- run timestamp

---

## Go / no-go guidance

The system is ready to move from Polyvore to pilot client data when:

- retrieval slot purity is high
- outfit reranking is clearly better than unranked baselines
- explanations are mostly factual
- missing metadata recovery does not collapse performance
- failure modes are understood and logged
