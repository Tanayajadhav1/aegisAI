"""risk_engine package exports

Expose a single convenience function `analyze_prompt` for consumers.
"""
from .analyzer import analyze_prompt

__all__ = ["analyze_prompt"]
