"""Main classifier for gibberish detection."""

from src.gibberish.enums import InputVerdict
from src.gibberish.llm_fallback import apply_llm_override, classify_with_llm
from src.gibberish.logging_utils import log_classification_result
from src.gibberish.models import GibberishConfig, GibberishResult
from src.gibberish.normalization import normalize_text
from src.gibberish.rules import (
    check_hard_gibberish_rules,
    check_legal_safe_overrides,
    compute_heuristic_score,
    get_verdict_from_score,
)
from src.gibberish.text_stats import extract_text_stats


def classify_input(text: str, *, config: GibberishConfig = None) -> GibberishResult:
    """
    Classify user input as REAL, SUSPICIOUS, or GIBBERISH.
    
    This is a hybrid two-stage system:
    1. Deterministic fast-pass engine (cheap, fast, safe for Arabic)
    2. Optional LLM fallback (only for SUSPICIOUS cases)
    
    Args:
        text: Raw user input text
        config: GibberishConfig (defaults to GibberishConfig() if not provided)
        
    Returns:
        GibberishResult with classification verdict, score, and reasons
    """
    if config is None:
        config = GibberishConfig()
    
    # Step 1: Normalization
    normalized = normalize_text(text)
    if normalized is None:
        return GibberishResult(
            status=InputVerdict.GIBBERISH,
            score=0.0,
            reasons=["Empty or only whitespace/zero-width characters"],
            meta={'n': 0},
        )
    
    # Step 2: Extract text statistics
    stats = extract_text_stats(normalized)
    
    # Step 3: Check hard gibberish rules
    is_hard_gibberish, hard_reasons = check_hard_gibberish_rules(stats, normalized)
    if is_hard_gibberish:
        result = GibberishResult(
            status=InputVerdict.GIBBERISH,
            score=0.0,
            reasons=hard_reasons,
            meta={
                'n': stats.n,
                'r_letters': stats.r_letters,
                'r_punct': stats.r_punct,
                'longest_run': stats.longest_run,
            },
        )
        log_classification_result(result, stats)
        return result
    
    # Step 4: Check legal safe overrides
    is_legal, legal_reasons = check_legal_safe_overrides(normalized, stats)
    if is_legal:
        result = GibberishResult(
            status=InputVerdict.REAL,
            score=1.0,
            reasons=legal_reasons,
            meta={
                'n': stats.n,
                'r_letters': stats.r_letters,
                'r_punct': stats.r_punct,
                'override': 'legal',
            },
        )
        log_classification_result(result, stats)
        return result
    
    # Step 5: Heuristic scoring
    score, score_reasons = compute_heuristic_score(stats, normalized)
    verdict = get_verdict_from_score(score, config)
    
    result = GibberishResult(
        status=verdict,
        score=score,
        reasons=score_reasons,
        meta={
            'n': stats.n,
            'r_letters': stats.r_letters,
            'r_punct': stats.r_punct,
            'wc': stats.wc,
            'unique_ratio': stats.unique_ratio,
        },
    )
    
    # Step 6: Optional LLM fallback (only for SUSPICIOUS cases)
    if verdict == InputVerdict.SUSPICIOUS and config.llm_enabled:
        llm_result = classify_with_llm(normalized, config)
        if llm_result:
            original_verdict = verdict
            verdict = apply_llm_override(verdict, llm_result, config)
            
            if verdict != original_verdict:
                result.reasons.append(f"LLM override: {llm_result.get('reason', 'N/A')} (confidence: {llm_result.get('confidence', 0.0):.2f})")
                result.status = verdict
                result.meta['llm_override'] = True
                result.meta['llm_confidence'] = llm_result.get('confidence', 0.0)
            else:
                result.meta['llm_override'] = False
    
    log_classification_result(result, stats)
    return result

