import os
from typing import Optional, Dict, Any

_classifier = None
_model_dir = os.environ.get("RISK_MODEL_PATH", "./my_risk_model")


def _load_classifier(model_dir: str):
    global _classifier
    try:
        from transformers import pipeline
    except Exception as e:
        raise RuntimeError("transformers package is required for ML detection: " + str(e))
    # Resolve to an absolute path and ensure the directory exists. This avoids
    # repo-id validation errors when passing relative paths like './my_risk_model'.
    model_dir = os.path.abspath(model_dir)
    if not os.path.isdir(model_dir):
        raise RuntimeError(f"Model directory not found: {model_dir}")

    # Use a text-classification pipeline pointing at the local model directory
    _classifier = pipeline(
        "text-classification",
        model=model_dir,
        tokenizer=model_dir,
    )


def set_model_path(path: str):
    """Set the local model path to load from. Use this if you place the
    extracted model archive into a project folder.

    Example: set_model_path("risk_engine/models/my_risk_model")
    """
    global _model_dir
    _model_dir = path


def predict(text: str) -> Dict[str, Any]:
    """Run the ML prompt-injection classifier on `text`.

    Returns a dict: {"label": 0|1, "score": float, "name": "SAFE"|"PROMPT_INJECTION"}
    If the model or `transformers` are not available, returns a safe default
    with an `error` key describing the problem.
    """
    global _classifier

    if _classifier is None:
        # lazy-load the classifier
        try:
            _load_classifier(_model_dir)
        except Exception as e:
            return {"label": 0, "score": 0.0, "name": "SAFE", "error": str(e)}

    try:
        out = _classifier(text)
        if isinstance(out, list) and len(out) > 0:
            entry = out[0]
            label_str = entry.get("label", "LABEL_0")
            score = float(entry.get("score", 0.0))

            # Hugging Face maps numeric labels to LABEL_{i}; map LABEL_0->0, LABEL_1->1
            label_num = 1 if label_str.endswith("1") else 0
            name = "PROMPT_INJECTION" if label_num == 1 else "SAFE"

            return {"label": label_num, "score": score, "name": name}
        else:
            return {"label": 0, "score": 0.0, "name": "SAFE", "error": "unexpected pipeline output"}
    except Exception as e:
        return {"label": 0, "score": 0.0, "name": "SAFE", "error": str(e)}
