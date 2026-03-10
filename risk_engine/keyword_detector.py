import re


SENSITIVE_KEYWORDS = [
    # common secrets and keys
    "password",
    "api key",
    "private key",
    "secret",
    "secret project",

    # sensitive business terms (added per user request)
    "confidential",
    "internal",
    "internal data",
    "proprietary",
    "strategy",
    "client",
    "financial",
    "pricing",
    "roadmap",
]


def detect_keywords(prompt: str):
    """Return a list of sensitive keywords found in `prompt` (case-insensitive).

    Uses word-boundary regex matching so that words like "internal" and
    multi-word phrases such as "secret project" are matched robustly.
    """

    hits = []

    for keyword in SENSITIVE_KEYWORDS:
        pattern = r"\b" + re.escape(keyword) + r"\b"
        if re.search(pattern, prompt, flags=re.IGNORECASE):
            hits.append(keyword)

    return hits