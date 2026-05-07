"""Offline metrics for the retrieval and composition pipeline.

Covers the evaluation harness required by the shared foundation:
- retrieval precision by slot
- top-k hit rate
- fill-in-the-blank retrieval accuracy
- compatibility ranking quality
"""
from __future__ import annotations

from typing import Iterable, List, Sequence


def retrieval_precision_at_k(retrieved_ids: Sequence[str], relevant_ids: set, k: int) -> float:
    if k <= 0:
        return 0.0
    topk = retrieved_ids[:k]
    return sum(1 for i in topk if i in relevant_ids) / k


def hit_rate_at_k(retrieved_ids: Sequence[str], target_id: str, k: int) -> float:
    return 1.0 if target_id in list(retrieved_ids)[:k] else 0.0


def fitb_accuracy(predictions: Iterable[bool]) -> float:
    preds = list(predictions)
    return sum(preds) / len(preds) if preds else 0.0


def mean_reciprocal_rank(ranked_ids: Sequence[str], target_id: str) -> float:
    for i, rid in enumerate(ranked_ids, start=1):
        if rid == target_id:
            return 1.0 / i
    return 0.0


def compatibility_ranking_score(scores: List[float], ground_truth: List[float]) -> float:
    """Rudimentary Spearman-like correlation without scipy."""
    if len(scores) != len(ground_truth) or not scores:
        return 0.0
    order_pred = sorted(range(len(scores)), key=lambda i: -scores[i])
    order_true = sorted(range(len(ground_truth)), key=lambda i: -ground_truth[i])
    rank_pred = {idx: r for r, idx in enumerate(order_pred)}
    rank_true = {idx: r for r, idx in enumerate(order_true)}
    n = len(scores)
    d2 = sum((rank_pred[i] - rank_true[i]) ** 2 for i in range(n))
    return 1 - (6 * d2) / (n * (n * n - 1)) if n > 1 else 0.0
