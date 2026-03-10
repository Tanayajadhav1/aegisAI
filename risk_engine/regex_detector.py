import re

REGEX_PATTERNS = {
    "credit_card": r"\b(?:\d[ -]*?){13,16}\b",
    "aws_key": r"AKIA[0-9A-Z]{14,20}",
    "generic_api_key": r"\b[A-Za-z0-9_\-]{20,45}\b",
    "sk_api_key": r"sk-[A-Za-z0-9]{20,}",
    "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
    "password_assignment": r"(password|passwd|pwd)\s*[:=]\s*\S+"
}

def detect_regex(prompt):

    matches = []

    for name, pattern in REGEX_PATTERNS.items():

        found = re.findall(pattern, prompt)

        if found:
            matches.append({
                "type": name,
                "matches": found
            })

    return matches
