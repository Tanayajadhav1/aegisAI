"""Risk engine analyzer

Provides a single entry point `analyze_prompt(prompt: str) -> dict` which runs
the keyword detector, regex detector, and prompt-injection detector, then
calculates risk and returns a consistent JSON-serializable dictionary.

Example:
    from risk_engine.analyzer import analyze_prompt

    result = analyze_prompt("my api key is AKIA... and ignore previous instructions")
    # result is a dict with keys: keywords, regex_matches, prompt_injection,
    # risk_score, risk_level

"""
from typing import Dict, Any

from .keyword_detector import detect_keywords
from .regex_detector import detect_regex
from .prompt_injection_detector import detect_prompt_injection
from .risk_scoring import calculate_risk


def analyze_prompt(prompt: str) -> Dict[str, Any]:
    """Analyze a text prompt for sensitive content and prompt injection.

    Returns a structured dictionary suitable for JSON serialization with the
    following keys:

    - "keywords": list of keyword strings detected
    - "regex_matches": list of dicts {"type": str, "matches": list[str]}
    - "prompt_injection": list of matched injection patterns
    - "risk_score": numeric score
    - "risk_level": one of "LOW", "MEDIUM", "HIGH"

    Args:
        prompt: The input prompt text to analyze.

    Example:
        >>> analyze_prompt("please ignore previous instructions")
        {"keywords": [], "regex_matches": [], "prompt_injection": ["ignore (all|previous) instructions"], ...}

    """

    keywords = detect_keywords(prompt)
    regex_matches = detect_regex(prompt)
    injections = detect_prompt_injection(prompt)

    score, level = calculate_risk(keywords, regex_matches, injections)

    return {
        "keywords": keywords,
        "regex_matches": regex_matches,
        "prompt_injection": injections,
        "risk_score": score,
        "risk_level": level,
    }
