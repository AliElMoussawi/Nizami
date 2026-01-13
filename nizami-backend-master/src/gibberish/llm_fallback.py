"""Optional LLM fallback for borderline gibberish cases."""

import logging
from typing import Any, Dict, Optional

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

from src import settings
from src.gibberish.enums import InputVerdict
from src.gibberish.models import GibberishConfig

logger = logging.getLogger(__name__)


class LLMClassificationResponse(BaseModel):
    """Structured response from LLM classifier."""
    label: str = Field(description="Classification label: 'real' or 'gibberish'")
    confidence: float = Field(description="Confidence score between 0 and 1", ge=0.0, le=1.0)
    reason: str = Field(description="Brief explanation for the classification")


def classify_with_llm(text: str, config: GibberishConfig) -> Optional[Dict[str, Any]]:
    """
    Use LLM to classify suspicious input.
    
    Args:
        text: Input text to classify
        config: GibberishConfig
        
    Returns:
        Dict with 'label', 'confidence', 'reason', or None if LLM call fails
    """
    if not config.llm_enabled or not settings.OPENAI_API_KEY:
        return None
    
    try:
        # Create LLM with structured output
        llm = ChatOpenAI(
            openai_api_key=settings.OPENAI_API_KEY,
            model_name='gpt-4o-mini',
            temperature=0.1,
            request_timeout=10,  # Fast timeout for this check
        )
        
        structured_llm = llm.with_structured_output(LLMClassificationResponse)
        
        system_prompt = """You are a text classification assistant for a legal AI platform.
Your task is to determine if the given text is meaningful legal content or gibberish.

Meaningful legal content includes:
- Valid Arabic legal queries (e.g., "المادة 74", "ما هي شروط العقد")
- Valid English legal queries (e.g., "Article 74", "What are contract terms")
- Mixed Arabic-English legal content
- Short but meaningful legal prompts (e.g., "المادة", "Article 74")
- OCR-style legal input with minor errors
- Legal document snippets, case references, contract clauses

Gibberish includes:
- Keyboard mashing (e.g., "asdfkjasdfkjasd")
- Symbol spam (e.g., "%%%%%%%@@@@@@")
- Nonsense character repetition (e.g., "هههههههههههه")
- Junk bot input
- Meaningless character sequences

IMPORTANT: Arabic is a first-class legal language. Do NOT classify valid Arabic text as gibberish.
Be especially careful with short Arabic legal terms like "المادة" (article).

Respond with:
- label: "real" if meaningful legal content, "gibberish" if junk
- confidence: Your confidence level (0.0 to 1.0)
- reason: Brief explanation"""
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"Classify this text: {text}"),
        ]
        
        response = structured_llm.invoke(messages)
        
        return {
            'label': response.label.lower(),
            'confidence': response.confidence,
            'reason': response.reason,
        }
        
    except Exception as e:
        logger.warning(f"LLM classification failed: {e}", exc_info=True)
        return None


def apply_llm_override(
    current_verdict: InputVerdict,
    llm_result: Dict[str, Any],
    config: GibberishConfig
) -> InputVerdict:
    """
    Apply LLM override to current verdict if confidence is high enough.
    
    Args:
        current_verdict: Current classification verdict
        llm_result: LLM classification result
        config: GibberishConfig
        
    Returns:
        Updated verdict (or original if override conditions not met)
    """
    if not llm_result:
        return current_verdict
    
    label = llm_result.get('label', '').lower()
    confidence = llm_result.get('confidence', 0.0)
    
    # Only override if confidence is high enough
    if label == 'gibberish' and confidence >= config.llm_gibberish_confidence:
        return InputVerdict.GIBBERISH
    elif label == 'real' and confidence >= config.llm_real_confidence:
        return InputVerdict.REAL
    
    # Otherwise keep current verdict
    return current_verdict

