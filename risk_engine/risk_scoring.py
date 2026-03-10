def calculate_risk(keyword_hits, regex_hits, injection_hits):
    """Calculate a numeric risk score and map to a risk level.

    Scoring is simple weighted count of hits. Thresholds:
      - LOW: score < 20
      - MEDIUM: 20 <= score < 60
      - HIGH: score >= 60

    Returns a tuple of (score:int, level:str)
    """

    score = 0

    # scoring weights
    score += len(keyword_hits) * 20
    score += len(regex_hits) * 40
    score += len(injection_hits) * 50

    if score >= 60:
        level = "HIGH"
    elif score >= 20:
        level = "MEDIUM"
    else:
        level = "LOW"

    return score, level