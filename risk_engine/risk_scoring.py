def calculate_risk(keyword_hits, regex_hits, injection_hits, ml_prediction=None):

    score = 0

    # rule-based scoring
    score += len(keyword_hits) * 10
    score += len(regex_hits) * 40
    score += len(injection_hits) * 50

    # ML contribution
    if ml_prediction and isinstance(ml_prediction, dict):
        try:
            ml_score = float(ml_prediction.get("score", 0.0))
            ml_label = int(ml_prediction.get("label", 0))
        except Exception:
            ml_score = 0.0
            ml_label = 0

        if ml_label == 1:  # only apply when ML actually flagged risk
            if ml_score > 0.75:
                score += 40
            elif ml_score > 0.55:
                score += 15

    score = min(score, 100)

    if score >= 60:
        level = "HIGH"
    elif score >= 20:
        level = "MEDIUM"
    else:
        level = "LOW"

    return score, level