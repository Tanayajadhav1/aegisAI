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

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .keyword_detector import detect_keywords
from .regex_detector import detect_regex
from .prompt_injection_detector import detect_prompt_injection
from .risk_scoring import calculate_risk

# ──────────────────────────────────────────────
# FastAPI app
# ──────────────────────────────────────────────

app = FastAPI(
    title="AegisAI Risk Engine",
    description="AI Governance Firewall – prompt risk analysis API",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class PromptPayload(BaseModel):
    prompt: str
    platform: str = "unknown"


@app.post("/analyze")
def analyze_endpoint(payload: PromptPayload) -> Dict[str, Any]:
    """
    Receives a captured prompt from the proxy interceptor or test runner.
    Runs full risk analysis and returns a structured result.

    Called automatically by proxy_interceptor.py whenever a prompt is
    captured from ChatGPT, Claude, Gemini, Perplexity, or Copilot.
    """
    result = analyze_prompt(payload.prompt)

    action = "BLOCK" if result["risk_score"] >= 50 else "ALLOW"

    # Terminal output so every captured prompt is visible live
    print(f"\n[AegisAI] Platform      : {payload.platform}")
    print(f"          Risk Score    : {result['risk_score']}  ({result['risk_level']})")
    print(f"          Action        : {action}")
    print(f"          Keywords      : {result['keywords']}")
    print(f"          Regex Hits    : {[m['type'] for m in result['regex_matches']]}")
    print(f"          Injections    : {result['prompt_injection']}")
    print(f"          Prompt Preview: {payload.prompt[:120]}")

    return {
        "platform":       payload.platform,
        "risk_score":     result["risk_score"],
        "risk_level":     result["risk_level"],
        "keywords_found": result["keywords"],
        "regex_matches":  result["regex_matches"],
        "prompt_injection": result["prompt_injection"],
        "action":         action,
        "prompt_preview": payload.prompt[:200],
    }


@app.get("/health")
def health_check():
    """Quick check to confirm the backend is running."""
    return {"status": "ok", "service": "AegisAI Risk Engine"}


# ──────────────────────────────────────────────
# Core analysis function (unchanged, importable)
# ──────────────────────────────────────────────

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
    keywords      = detect_keywords(prompt)
    regex_matches = detect_regex(prompt)
    injections    = detect_prompt_injection(prompt)

    score, level  = calculate_risk(keywords, regex_matches, injections)

    return {
        "keywords":         keywords,
        "regex_matches":    regex_matches,
        "prompt_injection": injections,
        "risk_score":       score,
        "risk_level":       level,
    }