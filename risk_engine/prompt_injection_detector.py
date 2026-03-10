import re

INJECTION_PATTERNS = [
    r"ignore (all|previous) instructions",
    r"disregard the rules",
    r"reveal system prompt",
    r"print (the )?system prompt",
    r"show hidden instructions",
    r"show hidden prompts",
    r"reveal developer message",
    r"bypass safety",
    r"act as .* without restrictions",
    r"developer mode"
]

def detect_prompt_injection(prompt):

    hits = []

    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, prompt.lower()):
            hits.append(pattern)

    return hits