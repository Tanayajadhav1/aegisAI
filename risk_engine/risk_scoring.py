def calculate_risk(keyword_hits, regex_hits, injection_hits, ml_prediction=None):
    """
    Unified risk scoring that combines rule-based signals with ML semantic understanding.
    
    Design:
      - Rule signals drive [0-40] baseline score
      - ML label drives [0-60] semantic score
      - Final score = rule_score + ml_score (capped at 100)
    
    This ensures both the rule evidence AND semantic ML understanding directly
    influence the final risk assessment.
    """
    
    # Step 1: Rule-based scoring (baseline evidence)
    rule_score = 0
    rule_score += len(keyword_hits) * 10
    rule_score += len(regex_hits) * 40
    rule_score += len(injection_hits) * 50
    rule_score = min(rule_score, 40)  # Cap rule-based at 40
    
    # Step 2: Convert ML label to semantic score directly
    ml_score = 0
    if ml_prediction and isinstance(ml_prediction, dict):
        try:
            # Use final_label if zero-shot was triggered, otherwise use original label
            if ml_prediction.get("zero_shot_triggered", False):
                final_label = int(ml_prediction.get("final_label", 0))
            else:
                final_label = int(ml_prediction.get("label", 0))
            
            # Map ML label directly to score:
            #   LOW (0) → +0
            #   MEDIUM (1) → +30
            #   HIGH (2) → +60
            ml_score = final_label * 30
            
        except Exception:
            ml_score = 0
    
    # Step 3: Combine rule evidence + ML semantic understanding
    score = rule_score + ml_score
    score = min(score, 100)
    
    # Map combined score to risk level
    if score >= 60:
        level = "HIGH"
    elif score >= 20:
        level = "MEDIUM"
    else:
        level = "LOW"

    return score, level