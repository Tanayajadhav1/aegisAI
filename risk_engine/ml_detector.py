import os
from pathlib import Path
from typing import Dict, Any, Optional

_classifier = None
_zero_shot_classifier = None

# mapping from numeric prediction to human-readable risk names
# the model's labels (e.g. "LABEL_0"/"LABEL_1") are not very
# descriptive, so we convert them after inference.
risk_map = {
    0: "LOW",
    1: "MEDIUM",
    2: "HIGH",
}
# also build a reverse lookup so we can map descriptive names back to
# their numeric IDs; the pipeline may already return the descriptive
# string if the model config contains id2label as we updated earlier.
reverse_risk_map = {v: k for k, v in risk_map.items()}

# Zero-shot intent classification labels (security-focused, not intent-focused)
# These labels help determine if the prompt is asking for harmful information or seeking education
ZERO_SHOT_LABELS = [
    "Requesting dangerous or harmful information",
    "Educational or defensive security discussion", 
    "Benign or innocent request"
]

# Default model path: points to "my_risk_model" in the project root
BASE_DIR = Path(__file__).resolve().parent.parent
_model_dir = BASE_DIR / "my_risk_model"

# Configuration for zero-shot classifier
SAFE_CONFIDENCE_THRESHOLD = 0.9
ZERO_SHOT_MODEL = "facebook/bart-large-mnli"


def _load_classifier(model_dir: Path):
    """Load the Hugging Face text-classification pipeline from a local model folder."""
    global _classifier
    try:
        from transformers import pipeline
    except ImportError as e:
        raise RuntimeError("transformers package is required for ML detection: " + str(e))

    # Ensure absolute path and folder exists
    model_dir = Path(model_dir).resolve()
    if not model_dir.is_dir():
        raise RuntimeError(f"Model directory not found: {model_dir}")

    _classifier = pipeline(
        "text-classification",
        model=str(model_dir),
        tokenizer=str(model_dir),
    )


def _load_zero_shot_classifier():
    """Load the Hugging Face zero-shot classification pipeline."""
    global _zero_shot_classifier
    try:
        from transformers import pipeline
    except ImportError as e:
        raise RuntimeError("transformers package is required for zero-shot detection: " + str(e))

    _zero_shot_classifier = pipeline(
        "zero-shot-classification",
        model=ZERO_SHOT_MODEL,
    )


def set_model_path(path: str):
    """Set a custom path for the local model folder."""
    global _model_dir
    _model_dir = Path(path).resolve()
    # Reset classifier so it reloads from the new path
    global _classifier
    _classifier = None


def set_safe_confidence_threshold(threshold: float):
    """Set the confidence threshold for triggering zero-shot analysis on SAFE predictions."""
    global SAFE_CONFIDENCE_THRESHOLD
    SAFE_CONFIDENCE_THRESHOLD = threshold


def set_zero_shot_model(model_name: str):
    """Set a custom zero-shot model."""
    global ZERO_SHOT_MODEL, _zero_shot_classifier
    ZERO_SHOT_MODEL = model_name
    _zero_shot_classifier = None  # Reset classifier so it reloads


def predict(text: str, safe_threshold: Optional[float] = None) -> Dict[str, Any]:
    """
    Run the two-layer prompt classification with 3 risk levels:
    Layer 1: ML risk model (text-classification) - detects risk level (LOW, MEDIUM, HIGH)
    Layer 2: Zero-shot intent classifier (security-focused) - refines assessment
    
    Args:
        text: The prompt text to classify
        safe_threshold: Confidence threshold for triggering zero-shot on LOW risk predictions.
                       If None, uses SAFE_CONFIDENCE_THRESHOLD. Additionally, zero-shot
                       is triggered when security keywords are detected.
    
    Returns:
        Dict with keys:
            - label: numeric risk label from ML model (0=LOW, 1=MEDIUM, 2=HIGH)
            - name: human-readable ML risk name (LOW, MEDIUM, HIGH)
            - score: ML model confidence score
            - zero_shot_triggered: bool indicating if Layer 2 was used
            - zero_shot_analysis: (optional) dict with intent prediction if triggered
                - top_intent: highest-scoring security intent assessment
                - confidence: score for the top intent
                - all_intents: dict of all intent scores
            - final_label: final adjusted label after Layer 2 analysis (may differ from label)
            - final_name: final adjusted name after Layer 2 analysis
            - label_changed: bool indicating if Layer 2 corrected the label
            - final_risk: (optional) "CORRECTED_FP" or "CORRECTED_FN" if Layer 2 made a correction
            - final_risk_reason: (optional) explanation of why correction was made
    """
    global _classifier, _zero_shot_classifier
    
    if safe_threshold is None:
        safe_threshold = SAFE_CONFIDENCE_THRESHOLD

    # --- Layer 1: ML Risk Model ---
    if _classifier is None:
        try:
            _load_classifier(_model_dir)
        except Exception as e:
            return {
                "label": 0,
                "score": 0.0,
                "name": "LOW",
                "final_label": 0,
                "final_name": "LOW",
                "label_changed": False,
                "zero_shot_triggered": False,
                "error": f"ML model load error: {str(e)}"
            }

    try:
        out = _classifier(text)
        if isinstance(out, list) and len(out) > 0:
            entry = out[0]
            label_str = entry.get("label", "LABEL_0")
            score = float(entry.get("score", 0.0))

            # Normalize label format
            label_num = None
            if label_str.startswith("LABEL_"):
                try:
                    label_num = int(label_str.split("_")[-1])
                except Exception:
                    label_num = None

            if label_num is None:
                label_num = reverse_risk_map.get(label_str, 0)
                name = label_str
            else:
                name = risk_map.get(label_num, label_str)

            ml_result = {"label": label_num, "score": score, "name": name}
            
            # --- IMPROVEMENT 1 & 2 & FINAL: Pre-process ML prediction with confidence-based rules ---
            
            # Define security terms for MEDIUM protection
            security_terms = [
                'sql injection', 'xss', 'csrf', 'authentication', 'authorization', 'encryption',
                'vulnerability', 'exploit', 'attack', 'phishing', 'malware', 'payload', 'injection',
                'password', 'firewall', 'ransomware', 'trojan', 'worm', 'botnet', 'ddos', 'dos',
                'brute force', 'privilege escalation', 'buffer overflow', 'zero-day', 'ransomware',
                'penetration test', 'security audit', 'vulnerability scan', 'threat', 'vulnerability patch'
            ]
            
            # Define strong attack keywords for forcing HIGH (FINAL: Added "attack", strengthened)
            strong_attack_keywords = ['bypass', 'exploit', 'hack', 'override', 'crack', 'jailbreak', 
                                      'backdoor', 'malware', 'infiltrate', 'breach', 'unauthorized access',
                                      'attack', 'steal', 'exfiltrate', 'ransomware', 'trojan', 'worm']
            
            text_lower = text.lower()
            has_strong_attack_keywords = any(keyword in text_lower for keyword in strong_attack_keywords)
            has_security_terms = any(term in text_lower for term in security_terms)
            
            # FINAL IMPROVEMENT 2: Force HIGH if strong attack keywords present (HARD rule)
            if has_strong_attack_keywords and label_num < 2:
                label_num = 2
                name = "HIGH"
                ml_result["label"] = label_num
                ml_result["name"] = name
                ml_result["upgraded_to_high"] = True
            
            # IMPROVEMENT 1: If MEDIUM with very high confidence but no critical keywords, downgrade to LOW
            elif label_num == 1 and score > 0.95:
                # Check if it actually contains no dangerous/attack keywords
                if not has_strong_attack_keywords:
                    # Avoid false positives: downgrade high-confidence MEDIUM to LOW
                    label_num = 0
                    name = "LOW"
                    ml_result["label"] = label_num
                    ml_result["name"] = name
                    ml_result["downgraded_to_low"] = True
            
            # FINAL IMPROVEMENT 1: Protect MEDIUM from dropping to LOW
            # If LOW with 95%+ confidence but contains security terms, upgrade to MEDIUM
            elif label_num == 0 and score > 0.95 and has_security_terms and not has_strong_attack_keywords:
                label_num = 1
                name = "MEDIUM"
                ml_result["label"] = label_num
                ml_result["name"] = name
                ml_result["upgraded_to_medium"] = True
            
            # --- Layer 2: Zero-Shot Intent Classifier ---
            # Trigger zero-shot if: MEDIUM/HIGH risk OR low-confidence LOW
            # OR if the prompt contains security-related keywords (more aggressive triggering)
            security_keywords = [
                'bypass', 'exploit', 'vulnerability', 'hack', 'crack', 'password',
                'decrypt', 'penetration', 'malware', 'payload', 'injection', 'xss',
                'sql', 'extract', 'retrieve', 'unauthorized', 'restrict', 'override',
                'safeguard', 'jailbreak', 'prompt', 'system', 'admin', 'root', 'sudo',
                'shell', 'command', 'execute', 'reverse engineer', 'circumvent',
                'evade', 'evasion', 'detection', 'intrusion', 'firewall', 'iptables',
                'privilege escalation', 'escalate', 'elevation', 'unrestricted',
                'disable security', 'remove restriction', 'bypass', 'spoof', 'forge',
                'backdoor', 'trojan', 'worm', 'botnet', 'c2', 'command and control',
                'data exfiltration', 'steal', 'leak', 'phishing', 'social engineer'
            ]

            has_security_keywords = any(keyword in text_lower for keyword in security_keywords)
            
            # Detect highly suspicious keyword combinations (definite attack patterns)
            highly_suspicious_patterns = [
                ('evade', 'detection'),
                ('remove', 'restriction'),
                ('bypass', 'restrict'),
                ('privilege', 'escalat'),
                ('unauthorized', 'access'),
                ('backdoor', ''),  # Any mention of backdoor alone
                ('crack', 'password'),
                ('steal', 'data'),
            ]
            
            is_highly_suspicious = any(
                pattern[0] in text_lower and (not pattern[1] or pattern[1] in text_lower)
                for pattern in highly_suspicious_patterns
            )
            
            # Trigger zero-shot for MEDIUM/HIGH or low-confidence LOW
            should_trigger_zero_shot = (
                label_num >= 1 or  # MEDIUM or HIGH
                (label_num == 0 and score < safe_threshold) or  # LOW but low confidence
                has_security_keywords  # Contains security-related keywords
            )

            if should_trigger_zero_shot:
                try:
                    if _zero_shot_classifier is None:
                        _load_zero_shot_classifier()

                    zero_shot_result = _zero_shot_classifier(text, ZERO_SHOT_LABELS)
                    if isinstance(zero_shot_result, dict) and "labels" in zero_shot_result:
                        top_intent = zero_shot_result["labels"][0]
                        intent_score = float(zero_shot_result["scores"][0])

                        ml_result["zero_shot_analysis"] = {
                            "top_intent": top_intent,
                            "confidence": intent_score,
                            "all_intents": dict(zip(
                                zero_shot_result["labels"],
                                zero_shot_result["scores"]
                            ))
                        }
                        ml_result["zero_shot_triggered"] = True

                        # Refine final risk assessment based on zero-shot intent
                        # Map zero-shot labels to 3 risk levels:
                        #   "Benign or innocent request" = LOW (0)
                        #   "Educational or defensive security discussion" = MEDIUM (1)
                        #   "Requesting dangerous or harmful information" = HIGH (2)
                        
                        final_label = label_num
                        final_name = name
                        
                        all_intents = ml_result["zero_shot_analysis"]["all_intents"]
                        
                        # Extract scores for each label
                        dangerous_score = all_intents.get("Requesting dangerous or harmful information", 0)
                        educational_score = all_intents.get("Educational or defensive security discussion", 0)
                        benign_score = all_intents.get("Benign or innocent request", 0)
                        
                        # Determine final label based on highest intent probability
                        intent_scores = [
                            (0, benign_score, "Benign or innocent request"),
                            (1, educational_score, "Educational or defensive security discussion"),
                            (2, dangerous_score, "Requesting dangerous or harmful information"),
                        ]
                        intent_scores.sort(key=lambda x: x[1], reverse=True)
                        highest_intent_label, highest_intent_score = intent_scores[0][0], intent_scores[0][1]
                        
                        # HIGHEST PRIORITY: If highly suspicious patterns + ML flagged risky, ALWAYS keep risky
                        if is_highly_suspicious and label_num >= 1:
                            # Don't correct - keep the risky label
                            pass
                        
                        # Priority logic: When ML confidence is HIGH + dangerous keywords present,
                        # the model is likely making an informed decision about the risky nature.
                        # DO NOT override if:
                        #   - ML confidence is very high (>0.95) AND
                        #   - Prompt contains dangerous keywords AND
                        #   - Zero-shot shows even moderate dangerous intent (>0.1)
                        elif label_num >= 1 and has_security_keywords and score > 0.95 and dangerous_score > 0.1:
                            # KEEP the risky classification - strong ML signal + suspicious keywords
                            pass  # Don't correct
                        
                        # For true LOW predictions, use zero-shot to refine between LOW and MEDIUM
                        elif label_num == 0:
                            # If highly suspicious patterns detected, always bump to HIGH
                            if is_highly_suspicious:
                                final_label = 2
                                final_name = "HIGH"
                                ml_result["final_risk"] = "CORRECTED_FN"
                                ml_result["final_risk_reason"] = f"Highly suspicious keyword pattern detected despite LOW prediction"
                            # If dangerous keywords + dangerous intent, bump to MEDIUM or HIGH
                            elif has_security_keywords and dangerous_score > 0.4:
                                final_label = 2
                                final_name = "HIGH"
                                ml_result["final_risk"] = "CORRECTED_FN"
                                ml_result["final_risk_reason"] = f"Contains dangerous keywords with {dangerous_score:.2f} harmful intent score"
                            elif dangerous_score > 0.65:
                                # Strong dangerous signal = upgrade to HIGH
                                final_label = 2
                                final_name = "HIGH"
                                ml_result["final_risk"] = "CORRECTED_FN"
                                ml_result["final_risk_reason"] = f"Strong dangerous intent detected ({dangerous_score:.2f})"
                            elif educational_score > benign_score and educational_score > 0.5:
                                # Education-focused = MEDIUM
                                final_label = 1
                                final_name = "MEDIUM"
                        
                        # For MEDIUM predictions, check if should escalate to HIGH
                        elif label_num == 1:
                            if is_highly_suspicious or dangerous_score > 0.6:
                                final_label = 2
                                final_name = "HIGH"
                                ml_result["final_risk"] = "ESCALATED_RISK"
                                ml_result["final_risk_reason"] = f"Escalated from MEDIUM to HIGH due to intent analysis"
                            elif benign_score > 0.6 and dangerous_score < 0.2:
                                final_label = 0
                                final_name = "LOW"
                                ml_result["final_risk"] = "CORRECTED_FP"
                                ml_result["final_risk_reason"] = f"Benign intent detected despite MEDIUM prediction"
                        
                        # For HIGH predictions, only downgrade if clearly benign
                        elif label_num == 2:
                            # FINAL IMPROVEMENT 3: Trust HIGH predictions - NEVER downgrade unless absolutely sure
                            # If model predicted HIGH with high confidence, keep it for safety
                            if score > 0.9:
                                # Keep HIGH if model is very confident - safety first
                                pass
                            # Only downgrade if EXTREMELY benign (benign > 0.8 AND dangerous < 0.05)
                            elif benign_score > 0.8 and dangerous_score < 0.05 and not has_security_terms:
                                final_label = 0
                                final_name = "LOW"
                                ml_result["final_risk"] = "CORRECTED_FP"
                                ml_result["final_risk_reason"] = f"Clearly benign intent detected despite HIGH prediction"
                        
                        # Add final adjusted label
                        ml_result["final_label"] = final_label
                        ml_result["final_name"] = final_name
                        ml_result["label_changed"] = final_label != label_num

                    else:
                        ml_result["zero_shot_triggered"] = False
                        ml_result["zero_shot_error"] = "Unexpected zero-shot output format"

                except Exception as e:
                    ml_result["zero_shot_triggered"] = False
                    ml_result["zero_shot_error"] = str(e)
            else:
                ml_result["zero_shot_triggered"] = False
            
            # Always set final label (unchanged if zero-shot didn't trigger or correct)
            if "final_label" not in ml_result:
                ml_result["final_label"] = label_num
                ml_result["final_name"] = name
                ml_result["label_changed"] = False

            return ml_result
        else:
            return {
                "label": 0,
                "score": 0.0,
                "name": "LOW",
                "final_label": 0,
                "final_name": "LOW",
                "label_changed": False,
                "zero_shot_triggered": False,
                "error": "unexpected pipeline output"
            }
    except Exception as e:
        return {
            "label": 0,
            "score": 0.0,
            "name": "LOW",
            "final_label": 0,
            "final_name": "LOW",
            "label_changed": False,
            "zero_shot_triggered": False,
            "error": str(e)
        }