from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any


@dataclass
class NormalizedItem:
    item_id: str
    image_path_or_url: str
    title: Optional[str] = None
    description: Optional[str] = None
    raw_category: Optional[str] = None
    slot: Optional[str] = None
    subcategory: Optional[str] = None
    department: Optional[str] = None
    colors: List[str] = field(default_factory=list)
    material: Optional[str] = None
    pattern: Optional[str] = None
    season: Optional[str] = None
    occasion: Optional[str] = None
    brand: Optional[str] = None
    price: Optional[float] = None
    currency: Optional[str] = None
    stock_status: Optional[str] = None
    metadata_source: Dict[str, str] = field(default_factory=dict)
    extra: Dict[str, Any] = field(default_factory=dict)


@dataclass
class OutfitCandidate:
    seed_item_id: str
    item_ids: List[str]
    slot_map: Dict[str, str]
    retrieval_scores: Dict[str, float] = field(default_factory=dict)
    rerank_score: Optional[float] = None
    explanation: Optional[str] = None
    extra: Dict[str, Any] = field(default_factory=dict)
