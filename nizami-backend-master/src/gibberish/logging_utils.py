"""Privacy-aware logging utilities for gibberish detection."""

import logging
from typing import Any, Dict

from src.gibberish.models import GibberishResult
from src.gibberish.text_stats import TextStats

logger = logging.getLogger(__name__)


def log_classification_result(
    result: GibberishResult,
    stats: TextStats,
    include_reasons: bool = True,
) -> None:
    """
    Log classification result without raw user input.
    
    Only logs:
    - status
    - score
    - reasons (optional)
    - n (text length)
    - r_letters
    - r_punct
    
    Args:
        result: GibberishResult to log
        stats: TextStats used for classification
        include_reasons: Whether to include reasons in log
    """
    log_data: Dict[str, Any] = {
        'status': result.status.value,
        'score': result.score,
        'n': stats.n,
        'r_letters': round(stats.r_letters, 3),
        'r_punct': round(stats.r_punct, 3),
    }
    
    if include_reasons and result.reasons:
        log_data['reasons'] = result.reasons
    
    logger.info(f"Gibberish classification: {log_data}")

