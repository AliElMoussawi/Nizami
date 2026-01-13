"""Text normalization utilities for gibberish detection."""

import re
from typing import Optional


def normalize_text(text: str) -> Optional[str]:
    """
    Normalize text before classification.
    
    Steps:
    1. Strip and collapse whitespace
    2. Remove zero-width characters: \u200b \u200c \u200d \ufeff
    3. Do NOT remove punctuation
    
    Args:
        text: Raw input text
        
    Returns:
        Normalized text, or None if result is empty
    """
    if not text:
        return None
    
    # Remove zero-width characters
    zero_width_chars = '\u200b\u200c\u200d\ufeff'
    normalized = text.translate(str.maketrans('', '', zero_width_chars))
    
    # Collapse whitespace (spaces, tabs, newlines) to single spaces
    normalized = re.sub(r'\s+', ' ', normalized)
    
    # Strip leading/trailing whitespace
    normalized = normalized.strip()
    
    # Return None if empty after normalization
    if not normalized:
        return None
    
    return normalized

