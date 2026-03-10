SENSITIVE_KEYWORDS = [
    "password",
    "api key",
    "secret",
    "confidential",
    "internal data",
    "private key"
]

def detect_keywords(prompt):
    hits = []

    for keyword in SENSITIVE_KEYWORDS:
        if keyword.lower() in prompt.lower():
            hits.append(keyword)

    return hits