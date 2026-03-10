def calculate_risk(keyword_hits, regex_hits, injection_hits, ml_prediction=None):
    """Calculate a numeric risk score and map to a risk level.

    Scoring is a weighted count of hits. Thresholds:
      - LOW: score < 20
      - MEDIUM: 20 <= score < 60
      - HIGH: score >= 60

    `ml_prediction` may be provided as a dict {"label":0|1, "score":float} and
    will contribute proportionally to the risk when it detects `PROMPT_INJECTION`.

    Returns a tuple of (score:int, level:str)
    """

    score = 0

    # scoring weights (existing rule-based):
    score += len(keyword_hits) * 20
    score += len(regex_hits) * 40
    score += len(injection_hits) * 50

    # incorporate ML classifier result (if present)
    if ml_prediction and isinstance(ml_prediction, dict):
        try:
            ml_label = int(ml_prediction.get("label", 0))
            ml_conf = float(ml_prediction.get("score", 0.0))
        except Exception:
            ml_label = 0
            ml_conf = 0.0

        if ml_label == 1 and ml_conf > 0.0:
            # give ML detection a proportional boost (max ~50 points at conf==1.0)
            score += int(round(50 * ml_conf))

    # cap at 100 so endpoint action threshold (>=50) stays consistent
    score = min(score, 100)

    if score >= 60:
        level = "HIGH"
    elif score >= 20:
        level = "MEDIUM"
    else:
        level = "LOW"

    return score, level