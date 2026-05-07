"""Polyvore outfit dataset loader."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, Dict, Any


def load_polyvore_outfits(path: str | Path) -> Iterable[Dict[str, Any]]:
    path = Path(path)
    with path.open() as f:
        if path.suffix == ".json":
            yield from json.load(f)
        else:
            for line in f:
                line = line.strip()
                if line:
                    yield json.loads(line)
