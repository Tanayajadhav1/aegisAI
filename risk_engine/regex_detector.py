import re

REGEX_PATTERNS = {
    "credit_card": r"\b\d{16}\b",
    "aws_key": r"AKIA[0-9A-Z]{16}",
    "generic_api_key": r"sk-[A-Za-z0-9]{20,}",
    "email": r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"
}

def detect_regex(prompt):

    matches = []

    for name, pattern in REGEX_PATTERNS.items():
        if re.search(pattern, prompt):
            matches.append(name)

    return matches