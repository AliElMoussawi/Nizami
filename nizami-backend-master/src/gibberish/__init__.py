"""
Gibberish Detection System for Nizami Legal AI Platform.

A production-grade hybrid system for detecting gibberish input while safely
handling Arabic, English, and mixed legal content.
"""

from src.gibberish.classifier import classify_input
from src.gibberish.enums import InputVerdict
from src.gibberish.models import GibberishConfig, GibberishResult

__all__ = [
    'classify_input',
    'InputVerdict',
    'GibberishConfig',
    'GibberishResult',
]

