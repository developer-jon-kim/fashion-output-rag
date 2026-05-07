"""Polyvore item dataset loader.

Reads raw Polyvore items into an iterable of dicts. Downstream normalization
into `NormalizedItem` lives in `src/normalization/normalize_polyvore.py`.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, Dict, Any


def load_polyvore_items(path: str | Path) -> Iterable[Dict[str, Any]]:
    path = Path(path)
    if path.suffix == ".json":
        with path.open() as f:
            data = json.load(f)
        if isinstance(data, dict):
            data = list(data.values())
        yield from data
    elif path.suffix == ".jsonl":
        with path.open() as f:
            for line in f:
                line = line.strip()
                if line:
                    yield json.loads(line)
    else:
        raise ValueError(f"Unsupported item file format: {path.suffix}")
