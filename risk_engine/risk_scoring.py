def calculate_risk(keyword_hits, regex_hits, injection_hits):

    score = 0

    # scoring weights
    score += len(keyword_hits) * 20
    score += len(regex_hits) * 40
    score += len(injection_hits) * 50

    if score >= 10:
        level = "HIGH"
    elif score >= 5:
        level = "MEDIUM"
    else:
        level = "LOW"

    return score, level