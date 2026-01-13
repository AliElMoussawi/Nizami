"""Text statistics extraction for gibberish detection."""

import re
from dataclasses import dataclass
from typing import List


@dataclass
class TextStats:
    """Statistics extracted from text for classification."""
    n: int  # total characters
    letters: int  # Arabic + Latin
    arabic: int  # Arabic characters
    latin: int  # Latin characters
    digits: int  # 0-9 + Arabic-Indic
    spaces: int
    punct: int  # punctuation and other
    
    # Computed ratios
    r_letters: float  # letters / n
    r_punct: float  # punct / n
    r_ar: float  # arabic / max(1, letters)
    r_lat: float  # latin / max(1, letters)
    
    # Token statistics
    wc: int  # word count
    unique_ratio: float  # unique tokens / total tokens
    avg_token_len: float
    longest_run: int  # longest repeated character run


def extract_text_stats(text: str) -> TextStats:
    """
    Extract comprehensive statistics from text.
    
    Args:
        text: Normalized input text
        
    Returns:
        TextStats object with all computed metrics
    """
    n = len(text)
    
    # Character type counts
    arabic = 0
    latin = 0
    digits = 0
    spaces = 0
    punct = 0
    
    # Arabic Unicode ranges
    # Arabic: U+0600-U+06FF (includes Arabic-Indic digits)
    # Extended Arabic: U+0750-U+077F, U+08A0-U+08FF, U+FB50-U+FDFF, U+FE70-U+FEFF
    arabic_pattern = re.compile(
        r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]'
    )
    
    # Latin (ASCII letters)
    latin_pattern = re.compile(r'[a-zA-Z]')
    
    # Digits: 0-9 and Arabic-Indic (U+0660-U+0669)
    digit_pattern = re.compile(r'[0-9\u0660-\u0669]')
    
    # Spaces
    space_pattern = re.compile(r'\s')
    
    longest_run = 0
    current_run = 1
    prev_char = None
    
    for char in text:
        if arabic_pattern.match(char):
            arabic += 1
        elif latin_pattern.match(char):
            latin += 1
        elif digit_pattern.match(char):
            digits += 1
        elif space_pattern.match(char):
            spaces += 1
        else:
            punct += 1
        
        # Track longest repeated character run
        if char == prev_char:
            current_run += 1
            longest_run = max(longest_run, current_run)
        else:
            current_run = 1
        prev_char = char
    
    letters = arabic + latin
    
    # Compute ratios
    r_letters = letters / n if n > 0 else 0.0
    r_punct = punct / n if n > 0 else 0.0
    r_ar = arabic / max(1, letters) if letters > 0 else 0.0
    r_lat = latin / max(1, letters) if letters > 0 else 0.0
    
    # Token statistics
    tokens = text.split()
    wc = len(tokens)
    
    if wc > 0:
        unique_tokens = len(set(tokens))
        unique_ratio = unique_tokens / wc
        total_token_len = sum(len(token) for token in tokens)
        avg_token_len = total_token_len / wc
    else:
        unique_ratio = 0.0
        avg_token_len = 0.0
    
    return TextStats(
        n=n,
        letters=letters,
        arabic=arabic,
        latin=latin,
        digits=digits,
        spaces=spaces,
        punct=punct,
        r_letters=r_letters,
        r_punct=r_punct,
        r_ar=r_ar,
        r_lat=r_lat,
        wc=wc,
        unique_ratio=unique_ratio,
        avg_token_len=avg_token_len,
        longest_run=longest_run,
    )

