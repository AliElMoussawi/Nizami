"""
Example usage of the gibberish detection system.

This file demonstrates how to use the gibberish classifier in various scenarios.
"""

from src.gibberish import classify_input, InputVerdict, GibberishConfig


def example_basic_usage():
    """Basic usage examples."""
    print("=== Basic Usage ===\n")
    
    # Arabic legal query
    result = classify_input("المادة 74 من النظام")
    print(f"Input: 'المادة 74 من النظام'")
    print(f"Status: {result.status.value}")
    print(f"Score: {result.score:.2f}")
    print(f"Reasons: {result.reasons}\n")
    
    # English legal query
    result = classify_input("Article 74 of the law")
    print(f"Input: 'Article 74 of the law'")
    print(f"Status: {result.status.value}")
    print(f"Score: {result.score:.2f}\n")
    
    # Gibberish
    result = classify_input("asdfkjasdfkjasdfkjasd")
    print(f"Input: 'asdfkjasdfkjasdfkjasd'")
    print(f"Status: {result.status.value}")
    print(f"Score: {result.score:.2f}")
    print(f"Reasons: {result.reasons}\n")


def example_with_llm():
    """Example with LLM fallback enabled."""
    print("=== With LLM Fallback ===\n")
    
    config = GibberishConfig(llm_enabled=True)
    
    # Borderline case that might benefit from LLM
    result = classify_input("some borderline text that needs verification", config=config)
    print(f"Input: 'some borderline text that needs verification'")
    print(f"Status: {result.status.value}")
    print(f"Score: {result.score:.2f}")
    if 'llm_override' in result.meta:
        print(f"LLM Override: {result.meta.get('llm_override')}")
        if result.meta.get('llm_override'):
            print(f"LLM Confidence: {result.meta.get('llm_confidence', 0.0):.2f}\n")


def example_integration():
    """Example of integrating into a message processing flow."""
    print("=== Integration Example ===\n")
    
    def process_user_message(text: str):
        """Process user message with gibberish check."""
        result = classify_input(text)
        
        if result.status == InputVerdict.GIBBERISH:
            return {
                "error": "Invalid input. Please provide a valid legal question.",
                "status": "rejected"
            }
        elif result.status == InputVerdict.SUSPICIOUS:
            return {
                "warning": "Input may be unclear. Please rephrase your question.",
                "status": "warning",
                "proceed": True
            }
        else:
            return {
                "status": "accepted",
                "proceed": True
            }
    
    # Test cases
    test_cases = [
        "المادة 74 من النظام",
        "asdfkjasdfkjasd",
        "abc def",
    ]
    
    for text in test_cases:
        response = process_user_message(text)
        print(f"Input: '{text}'")
        print(f"Response: {response}\n")


if __name__ == "__main__":
    example_basic_usage()
    example_with_llm()
    example_integration()

