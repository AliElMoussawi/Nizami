"""Enums for gibberish detection system."""

import enum


class InputVerdict(enum.Enum):
    """Classification verdict for user input."""
    REAL = "real"
    SUSPICIOUS = "suspicious"
    GIBBERISH = "gibberish"

