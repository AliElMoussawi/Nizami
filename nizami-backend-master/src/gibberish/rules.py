"""Hard rules and heuristics for gibberish detection."""

import re
from typing import List, Tuple

from src.gibberish.enums import InputVerdict
from src.gibberish.text_stats import TextStats


# Legal keywords
ARABIC_LEGAL_KEYWORDS = [
  "نظام",
  "قانون",
  "لائحة",
  "قرار",
  "مرسوم",
  "أمر",
  "جهة",
  "وزارة",
  "هيئة",
  "دائرة",
  "محكمة",
  "قاضي",
  "دعوى",
  "قضية",
  "طعن",
  "استئناف",
  "تنفيذ",
  "حكم",
  "عقد",
  "التزام",
  "مسؤولية",
  "تعويض",
  "مخالفة",
  "جزاء",
  "غرامة",
  "ترخيص",
  "تصريح",
  "تسجيل",
  "اعتماد",
  "إلغاء",
  "إخطار",
  "تبليغ",
  "توكيل",
  "محامي",
  "مدعي",
  "مدعى عليه",
  "اختصاص",
  "ولاية",
  "جهة قضائية",
  "تنفيذية",
  "تشريعية",
  "رقابة",
  "تحقيق",
  "ضبط",
  "مصادرة",
  "التزام نظامي",
  "إبرام",
  "إنهاء",
  "سريان",
  "نفاذ"
]


ENGLISH_LEGAL_KEYWORDS = [
  "regulation",
  "law",
  "bylaw",
  "decision",
  "decree",
  "order",
  "authority",
  "ministry",
  "agency",
  "department",
  "court",
  "judge",
  "lawsuit",
  "case",
  "appeal",
  "enforcement",
  "judgment",
  "contract",
  "obligation",
  "liability",
  "compensation",
  "violation",
  "penalty",
  "fine",
  "license",
  "permit",
  "registration",
  "approval",
  "cancellation",
  "notification",
  "service of notice",
  "power of attorney",
  "lawyer",
  "plaintiff",
  "defendant",
  "jurisdiction",
  "authority",
  "judicial authority",
  "executive",
  "legislative",
  "oversight",
  "investigation",
  "seizure",
  "confiscation",
  "regulatory compliance",
  "execution",
  "termination",
  "validity",
  "entry into force"
]

# Regex patterns for legal content
LEGAL_PATTERNS = [
    re.compile(r'article\s*\d+', re.IGNORECASE),
    re.compile(r'section\s*\d+', re.IGNORECASE),
    re.compile(r'المادة\s*\d+', re.IGNORECASE),
    re.compile(r'مادة\s*\d+', re.IGNORECASE),
    re.compile(r'https?://', re.IGNORECASE),  # URLs
    re.compile(r'\b\w+\.(com|org|net|gov|edu)\b', re.IGNORECASE),  # Domain patterns
]


def check_hard_gibberish_rules(stats: TextStats, text: str = "") -> Tuple[bool, List[str]]:
    """
    Check hard rules that immediately classify as GIBBERISH.
    
    Args:
        stats: TextStats object
        text: Original text (for checking legal keywords)
    
    Returns:
        Tuple of (is_gibberish, reasons)
    """
    reasons = []
    
    # Rule 1: n >= 10 and longest_run >= 8
    if stats.n >= 10 and stats.longest_run >= 8:
        reasons.append(f"Long repeated character run ({stats.longest_run}) in text of length {stats.n}")
        return True, reasons
    
    # Rule 2: n >= 15 and r_punct >= 0.75
    if stats.n >= 15 and stats.r_punct >= 0.75:
        reasons.append(f"Excessive punctuation ratio ({stats.r_punct:.2f}) in text of length {stats.n}")
        return True, reasons
    
    # Rule 3: n >= 20 and r_letters <= 0.15
    if stats.n >= 20 and stats.r_letters <= 0.15:
        reasons.append(f"Too few letters ({stats.r_letters:.2f}) in text of length {stats.n}")
        return True, reasons
    
    # Rule 4: n >= 20 and spaces == 0 and r_letters >= 0.8 and unique_ratio >= 0.9
    if stats.n >= 20 and stats.spaces == 0 and stats.r_letters >= 0.8 and stats.unique_ratio >= 0.9:
        reasons.append(f"No spaces with high letter ratio and unique ratio in text of length {stats.n}")
        return True, reasons
    
    # Rule 5: Short keyboard-mashed text (gibberish Latin characters)
    # Single word, no spaces, all letters, no legal keywords, 5-20 chars
    if (stats.r_lat >= 0.9 and stats.spaces == 0 and stats.wc == 1 and 
        5 <= stats.n <= 20 and text):
        has_legal_keyword = any(keyword.lower() in text.lower() for keyword in ENGLISH_LEGAL_KEYWORDS)
        # Check if it looks like keyboard mashing (high unique ratio, no vowels pattern, etc.)
        if not has_legal_keyword:
            reasons.append(f"Short keyboard-mashed text ({stats.n} chars) with no legal keywords - gibberish")
            return True, reasons
    
    # Rule 6: Short random Arabic sequences (gibberish Arabic characters)
    # Single word, no spaces, all Arabic, no legal keywords, 5-15 chars
    if (stats.r_ar >= 0.9 and stats.spaces == 0 and stats.wc == 1 and 
        5 <= stats.n <= 15 and text):
        has_legal_keyword = any(keyword in text for keyword in ARABIC_LEGAL_KEYWORDS)
        if not has_legal_keyword:
            reasons.append(f"Short random Arabic sequence ({stats.n} chars) with no legal keywords - gibberish")
            return True, reasons
    
    # Rule 6b: Mixed Arabic-Latin gibberish (random characters from both scripts)
    # Mixed Arabic and Latin, no spaces, single word, no legal keywords, 8-30 chars
    if (stats.r_ar >= 0.2 and stats.r_lat >= 0.2 and stats.spaces == 0 and 
        stats.wc == 1 and 8 <= stats.n <= 30 and text):
        has_arabic_keyword = any(keyword in text for keyword in ARABIC_LEGAL_KEYWORDS)
        has_english_keyword = any(keyword.lower() in text.lower() for keyword in ENGLISH_LEGAL_KEYWORDS)
        if not has_arabic_keyword and not has_english_keyword:
            reasons.append(f"Mixed Arabic-Latin gibberish ({stats.n} chars) with no legal keywords - gibberish")
            return True, reasons
    
    # Rule 7: Arabic gibberish detection - single long Arabic word with no legal keywords
    # Check if it's mostly Arabic, no spaces, single word, and no legal keywords
    if (stats.r_ar >= 0.8 and stats.spaces == 0 and stats.wc == 1 and 
        stats.n >= 10 and text):
        # Check if it contains any legal keywords
        has_legal_keyword = any(keyword in text for keyword in ARABIC_LEGAL_KEYWORDS)
        if not has_legal_keyword:
            reasons.append(f"Single long Arabic word ({stats.n} chars) with no legal keywords - likely gibberish")
            return True, reasons
    
    # Rule 8: Arabic text with very high unique ratio but no structure (no spaces, no legal keywords)
    if (stats.r_ar >= 0.7 and stats.spaces == 0 and stats.unique_ratio >= 0.95 and 
        stats.n >= 15 and text):
        has_legal_keyword = any(keyword in text for keyword in ARABIC_LEGAL_KEYWORDS)
        if not has_legal_keyword:
            reasons.append(f"Arabic text with very high unique ratio ({stats.unique_ratio:.2f}) but no structure - likely gibberish")
            return True, reasons
    
    return False, reasons


def check_legal_safe_overrides(text: str, stats: TextStats) -> Tuple[bool, List[str]]:
    """
    Check if text should be forced to REAL due to legal content indicators.
    
    Returns:
        Tuple of (is_legal, reasons)
    """
    reasons = []
    text_lower = text.lower()
    
    # Check Arabic legal keywords
    for keyword in ARABIC_LEGAL_KEYWORDS:
        if keyword in text:
            reasons.append(f"Contains Arabic legal keyword: {keyword}")
            return True, reasons
    
    # Check English legal keywords
    for keyword in ENGLISH_LEGAL_KEYWORDS:
        if keyword in text_lower:
            reasons.append(f"Contains English legal keyword: {keyword}")
            return True, reasons
    
    # Check regex patterns
    for pattern in LEGAL_PATTERNS:
        if pattern.search(text):
            reasons.append(f"Matches legal pattern: {pattern.pattern}")
            return True, reasons
    
    # Heuristic: wc >= 6 and r_letters >= 0.35
    if stats.wc >= 6 and stats.r_letters >= 0.35:
        reasons.append(f"Sufficient word count ({stats.wc}) and letter ratio ({stats.r_letters:.2f})")
        return True, reasons
    
    return False, reasons


def compute_heuristic_score(stats: TextStats, text: str = "") -> Tuple[float, List[str]]:
    """
    Compute heuristic score for classification.
    
    Returns:
        Tuple of (score, reasons)
    """
    score = 0.0
    reasons = []
    
    # Bonuses
    if stats.r_letters >= 0.40:
        score += 0.30
        reasons.append(f"Good letter ratio: {stats.r_letters:.2f}")
    
    if stats.wc >= 4:
        score += 0.15
        reasons.append(f"Sufficient word count: {stats.wc}")
    
    if stats.spaces >= 1:
        score += 0.10
        reasons.append("Contains spaces")
    
    if stats.unique_ratio >= 0.60:
        score += 0.15
        reasons.append(f"Good unique ratio: {stats.unique_ratio:.2f}")
    
    if 2 <= stats.avg_token_len <= 12:
        score += 0.10
        reasons.append(f"Reasonable average token length: {stats.avg_token_len:.2f}")
    
    # Mixed Arabic + English bonus (only if it has legal keywords or proper structure)
    if stats.r_ar > 0.2 and stats.r_lat > 0.2:
        has_arabic_keyword = text and any(keyword in text for keyword in ARABIC_LEGAL_KEYWORDS)
        has_english_keyword = text and any(keyword.lower() in text.lower() for keyword in ENGLISH_LEGAL_KEYWORDS)
        has_spaces = stats.spaces > 0
        # Only give bonus if it has legal keywords or proper structure (spaces, multiple words)
        if has_arabic_keyword or has_english_keyword or (has_spaces and stats.wc >= 2):
            score += 0.10
            reasons.append("Mixed Arabic and English content")
    
    # Digits with words bonus
    if stats.digits >= 1 and stats.wc >= 2:
        score += 0.10
        reasons.append("Contains digits with multiple words")
    
    # Penalties
    if stats.r_punct > 0.50:
        score -= 0.20
        reasons.append(f"High punctuation ratio: {stats.r_punct:.2f}")
    
    if stats.wc == 1 and stats.avg_token_len < 3:
        score -= 0.15
        reasons.append(f"Single short token: length {stats.avg_token_len:.2f}")
    
    # Penalty for single long Arabic word (likely gibberish) - only if no legal keywords
    if stats.wc == 1 and stats.r_ar >= 0.8 and stats.avg_token_len >= 10:
        has_legal_keyword = text and any(keyword in text for keyword in ARABIC_LEGAL_KEYWORDS)
        if not has_legal_keyword:
            score -= 0.25
            reasons.append(f"Single long Arabic word ({stats.avg_token_len:.1f} chars) with no legal keywords - likely gibberish")
    
    if stats.unique_ratio < 0.30 and stats.wc >= 4:
        score -= 0.15
        reasons.append(f"Low unique ratio: {stats.unique_ratio:.2f}")
    
    # Penalty for Arabic text with no spaces and no legal structure
    if stats.r_ar >= 0.7 and stats.spaces == 0 and stats.wc == 1 and stats.n >= 10:
        has_legal_keyword = text and any(keyword in text for keyword in ARABIC_LEGAL_KEYWORDS)
        if not has_legal_keyword:
            score -= 0.20
            reasons.append("Arabic text with no spaces and no legal keywords - suspicious")
    
    # Heavy penalty for mixed Arabic-Latin gibberish (random characters from both scripts)
    if (stats.r_ar >= 0.2 and stats.r_lat >= 0.2 and stats.spaces == 0 and 
        stats.wc == 1 and 8 <= stats.n <= 30):
        has_arabic_keyword = text and any(keyword in text for keyword in ARABIC_LEGAL_KEYWORDS)
        has_english_keyword = text and any(keyword.lower() in text.lower() for keyword in ENGLISH_LEGAL_KEYWORDS)
        if not has_arabic_keyword and not has_english_keyword:
            score -= 0.40
            reasons.append("Mixed Arabic-Latin text with no spaces and no legal keywords - likely gibberish")
    
    # Clamp score
    score = min(max(score, 0.0), 1.0)
    
    return score, reasons


def get_verdict_from_score(score: float, config) -> InputVerdict:
    """
    Convert heuristic score to verdict.
    
    Args:
        score: Heuristic score (0.0 to 1.0)
        config: GibberishConfig with thresholds
        
    Returns:
        InputVerdict
    """
    if score >= config.real_threshold:
        return InputVerdict.REAL
    elif score >= config.suspicious_threshold:
        return InputVerdict.SUSPICIOUS
    else:
        return InputVerdict.GIBBERISH

