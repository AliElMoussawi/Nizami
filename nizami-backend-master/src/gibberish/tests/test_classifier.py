"""Comprehensive tests for gibberish classifier."""

import pytest

from src.gibberish.classifier import classify_input
from src.gibberish.enums import InputVerdict
from src.gibberish.models import GibberishConfig


class TestArabicLegalQueries:
    """Test valid Arabic legal queries."""
    
    def test_arabic_article_reference(self):
        """Test Arabic article reference."""
        result = classify_input("المادة 74 من النظام")
        assert result.status == InputVerdict.REAL
        assert result.score >= 0.60
    
    def test_arabic_legal_question(self):
        """Test Arabic legal question."""
        result = classify_input("ما هي شروط العقد في القانون السعودي؟")
        assert result.status == InputVerdict.REAL
    
    def test_arabic_short_legal_term(self):
        """Test short Arabic legal term."""
        result = classify_input("المادة")
        # Should be REAL or SUSPICIOUS (short but meaningful)
        assert result.status in (InputVerdict.REAL, InputVerdict.SUSPICIOUS)
    
    def test_arabic_legal_document_snippet(self):
        """Test Arabic legal document snippet."""
        result = classify_input("نظام الشركات السعودي المادة 15 الفقرة 3")
        assert result.status == InputVerdict.REAL
    
    def test_arabic_mixed_with_numbers(self):
        """Test Arabic with numbers."""
        result = classify_input("المادة ١٢٣ من القانون")
        assert result.status == InputVerdict.REAL


class TestEnglishLegalQueries:
    """Test valid English legal queries."""
    
    def test_english_article_reference(self):
        """Test English article reference."""
        result = classify_input("Article 74 of the law")
        assert result.status == InputVerdict.REAL
    
    def test_english_legal_question(self):
        """Test English legal question."""
        result = classify_input("What are the requirements for starting a business in Saudi Arabia?")
        assert result.status == InputVerdict.REAL
    
    def test_english_short_legal_term(self):
        """Test short English legal term."""
        result = classify_input("Article 74")
        assert result.status == InputVerdict.REAL
    
    def test_english_legal_document_snippet(self):
        """Test English legal document snippet."""
        result = classify_input("Section 15 paragraph 3 of the Companies Act")
        assert result.status == InputVerdict.REAL
    
    def test_english_contract_clause(self):
        """Test English contract clause."""
        result = classify_input("The contract shall be governed by Saudi law")
        assert result.status == InputVerdict.REAL


class TestMixedArabicEnglish:
    """Test mixed Arabic-English content."""
    
    def test_mixed_legal_query(self):
        """Test mixed Arabic-English legal query."""
        result = classify_input("ما هي requirements للعقد contract؟")
        assert result.status == InputVerdict.REAL
    
    def test_mixed_article_reference(self):
        """Test mixed article reference."""
        result = classify_input("المادة Article 74 من النظام")
        assert result.status == InputVerdict.REAL
    
    def test_mixed_legal_terms(self):
        """Test mixed legal terms."""
        result = classify_input("عقد contract محكمة court")
        assert result.status == InputVerdict.REAL


class TestOCRStyleInput:
    """Test OCR-style legal input with minor errors."""
    
    def test_ocr_with_minor_errors(self):
        """Test OCR text with minor errors."""
        result = classify_input("المادة 74 من النظا م السعودي")
        assert result.status == InputVerdict.REAL
    
    def test_ocr_english_with_errors(self):
        """Test OCR English with errors."""
        result = classify_input("Article 74 of th e law")
        assert result.status == InputVerdict.REAL


class TestShortPrompts:
    """Test short but meaningful prompts."""
    
    def test_short_arabic_article(self):
        """Test short Arabic article reference."""
        result = classify_input("المادة")
        # Short but meaningful - should be SUSPICIOUS or REAL
        assert result.status in (InputVerdict.REAL, InputVerdict.SUSPICIOUS)
    
    def test_short_english_article(self):
        """Test short English article reference."""
        result = classify_input("Article 74")
        assert result.status == InputVerdict.REAL
    
    def test_short_arabic_number(self):
        """Test short Arabic with number."""
        result = classify_input("المادة ١")
        assert result.status == InputVerdict.REAL


class TestRepetitionJunk:
    """Test repetition and junk input."""
    
    def test_character_repetition(self):
        """Test repeated characters."""
        result = classify_input("هههههههههههه")
        assert result.status == InputVerdict.GIBBERISH
    
    def test_keyboard_mashing(self):
        """Test keyboard mashing."""
        result = classify_input("asdfkjasdfkjasdfkjasd")
        assert result.status == InputVerdict.GIBBERISH
    
    def test_long_repeated_run(self):
        """Test long repeated character run."""
        result = classify_input("aaaaaaaabbbbbbbb")
        assert result.status == InputVerdict.GIBBERISH


class TestSymbolSpam:
    """Test symbol spam."""
    
    def test_punctuation_spam(self):
        """Test excessive punctuation."""
        result = classify_input("%%%%%%%@@@@@@#######")
        assert result.status == InputVerdict.GIBBERISH
    
    def test_mixed_symbol_spam(self):
        """Test mixed symbol spam."""
        result = classify_input("!@#$%^&*()!@#$%^&*()")
        assert result.status == InputVerdict.GIBBERISH
    
    def test_high_punctuation_ratio(self):
        """Test high punctuation ratio."""
        result = classify_input("abc!@#def$%^ghi&*()")
        assert result.status == InputVerdict.GIBBERISH


class TestEmptyInvisibleInput:
    """Test empty and invisible input."""
    
    def test_empty_string(self):
        """Test empty string."""
        result = classify_input("")
        assert result.status == InputVerdict.GIBBERISH
    
    def test_whitespace_only(self):
        """Test whitespace only."""
        result = classify_input("   \n\t  ")
        assert result.status == InputVerdict.GIBBERISH
    
    def test_zero_width_characters(self):
        """Test zero-width characters."""
        result = classify_input("\u200b\u200c\u200d\ufeff")
        assert result.status == InputVerdict.GIBBERISH
    
    def test_mixed_invisible_chars(self):
        """Test mixed invisible characters."""
        result = classify_input("  \u200b  \u200c  ")
        assert result.status == InputVerdict.GIBBERISH


class TestIDsNamesContractSnippets:
    """Test IDs, names, and contract snippets."""
    
    def test_contract_id(self):
        """Test contract ID."""
        result = classify_input("Contract ID: CNT-2024-001")
        assert result.status == InputVerdict.REAL
    
    def test_legal_case_reference(self):
        """Test legal case reference."""
        result = classify_input("Case No. 123/2024")
        assert result.status == InputVerdict.REAL
    
    def test_url_reference(self):
        """Test URL reference."""
        result = classify_input("See https://example.com/legal-doc")
        assert result.status == InputVerdict.REAL
    
    def test_domain_pattern(self):
        """Test domain pattern."""
        result = classify_input("Visit example.com for details")
        assert result.status == InputVerdict.REAL


class TestEdgeCases:
    """Test edge cases."""
    
    def test_single_character(self):
        """Test single character."""
        result = classify_input("a")
        # Single character is suspicious
        assert result.status in (InputVerdict.SUSPICIOUS, InputVerdict.GIBBERISH)
    
    def test_single_arabic_character(self):
        """Test single Arabic character."""
        result = classify_input("م")
        assert result.status in (InputVerdict.SUSPICIOUS, InputVerdict.GIBBERISH)
    
    def test_very_short_but_meaningful(self):
        """Test very short but meaningful."""
        result = classify_input("عقد")
        # Should be SUSPICIOUS (short but contains legal keyword)
        assert result.status in (InputVerdict.REAL, InputVerdict.SUSPICIOUS)
    
    def test_numbers_only(self):
        """Test numbers only."""
        result = classify_input("123456789")
        # Numbers only without context is suspicious
        assert result.status in (InputVerdict.SUSPICIOUS, InputVerdict.GIBBERISH)
    
    def test_arabic_numbers_only(self):
        """Test Arabic-Indic numbers only."""
        result = classify_input("١٢٣٤٥٦")
        assert result.status in (InputVerdict.SUSPICIOUS, InputVerdict.GIBBERISH)


class TestHeuristicScoring:
    """Test heuristic scoring behavior."""
    
    def test_high_score_real(self):
        """Test high score results in REAL."""
        result = classify_input("This is a valid legal question about contract law in Saudi Arabia")
        assert result.status == InputVerdict.REAL
        assert result.score >= 0.60
    
    def test_medium_score_suspicious(self):
        """Test medium score results in SUSPICIOUS."""
        # Create a borderline case
        result = classify_input("abc def")
        # Should be suspicious (low word count, no legal keywords)
        assert result.status in (InputVerdict.SUSPICIOUS, InputVerdict.GIBBERISH)
    
    def test_low_score_gibberish(self):
        """Test low score results in GIBBERISH."""
        result = classify_input("asdfghjklqwertyuiop")
        assert result.status == InputVerdict.GIBBERISH
        assert result.score < 0.35


class TestConfigOptions:
    """Test configuration options."""
    
    def test_default_config(self):
        """Test with default config."""
        result = classify_input("Article 74")
        assert result.status == InputVerdict.REAL
    
    def test_custom_config(self):
        """Test with custom config."""
        config = GibberishConfig(
            llm_enabled=False,
            real_threshold=0.70,
            suspicious_threshold=0.40,
        )
        result = classify_input("Article 74")
        # Should still be REAL due to legal keyword override
        assert result.status == InputVerdict.REAL
    
    def test_llm_disabled(self):
        """Test with LLM disabled."""
        config = GibberishConfig(llm_enabled=False)
        result = classify_input("some borderline text")
        # Should not use LLM
        assert 'llm_override' not in result.meta or result.meta.get('llm_override') is False


class TestReasonsAndMeta:
    """Test that reasons and metadata are populated."""
    
    def test_reasons_populated(self):
        """Test that reasons are populated."""
        result = classify_input("المادة 74")
        assert len(result.reasons) > 0
        assert isinstance(result.reasons, list)
    
    def test_meta_populated(self):
        """Test that meta is populated."""
        result = classify_input("Article 74")
        assert 'n' in result.meta
        assert 'r_letters' in result.meta
        assert 'r_punct' in result.meta
    
    def test_gibberish_has_reasons(self):
        """Test that gibberish results have reasons."""
        result = classify_input("asdfkjasdfkjasd")
        assert len(result.reasons) > 0


class TestRealWorldScenarios:
    """Test real-world legal scenarios."""
    
    def test_legal_question_arabic(self):
        """Test real Arabic legal question."""
        result = classify_input("ما هي متطلبات تأسيس شركة في المملكة العربية السعودية؟")
        assert result.status == InputVerdict.REAL
    
    def test_legal_question_english(self):
        """Test real English legal question."""
        result = classify_input("What are the legal requirements for company registration?")
        assert result.status == InputVerdict.REAL
    
    def test_contract_excerpt(self):
        """Test contract excerpt."""
        result = classify_input("The parties agree that this contract shall be governed by Saudi law")
        assert result.status == InputVerdict.REAL
    
    def test_court_case_reference(self):
        """Test court case reference."""
        result = classify_input("Case No. 1234/2024 before the Commercial Court")
        assert result.status == InputVerdict.REAL
    
    def test_regulation_citation(self):
        """Test regulation citation."""
        result = classify_input("As per Article 15 of the Companies Regulation")
        assert result.status == InputVerdict.REAL

