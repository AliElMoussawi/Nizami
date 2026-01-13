"""Data models for gibberish detection system."""

from dataclasses import dataclass, field
from typing import Any, Dict, List

from src.gibberish.enums import InputVerdict


@dataclass
class GibberishConfig:
    """Configuration for gibberish detection."""
    llm_enabled: bool = False
    # Additional configurable thresholds can be added here
    real_threshold: float = 0.60
    suspicious_threshold: float = 0.35
    llm_gibberish_confidence: float = 0.70
    llm_real_confidence: float = 0.60


@dataclass
class GibberishResult:
    """Result of gibberish classification."""
    status: InputVerdict
    score: float
    reasons: List[str] = field(default_factory=list)
    meta: Dict[str, Any] = field(default_factory=dict)

