import os
from pathlib import Path
from typing import Dict, Any

_classifier = None

# mapping from numeric prediction to human-readable risk names
# the model's labels (e.g. "LABEL_0"/"LABEL_1") are not very
# descriptive, so we convert them after inference.
risk_map = {
    0: "SAFE",
    1: "PROMPT_INJECTION",
}
# also build a reverse lookup so we can map descriptive names back to
# their numeric IDs; the pipeline may already return the descriptive
# string if the model config contains id2label as we updated earlier.
reverse_risk_map = {v: k for k, v in risk_map.items()}

# Default model path: points to "my_risk_model" in the project root
BASE_DIR = Path(__file__).resolve().parent.parent
_model_dir = BASE_DIR / "my_risk_model"


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


def set_model_path(path: str):
    """Set a custom path for the local model folder."""
    global _model_dir
    _model_dir = Path(path).resolve()
    # Reset classifier so it reloads from the new path
    global _classifier
    _classifier = None


def predict(text: str) -> Dict[str, Any]:
    """Run the ML prompt-injection classifier on `text`."""
    global _classifier

    if _classifier is None:
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

            # the pipeline may return one of several formats depending on the
            # model config:
            #  * a generic string such as "LABEL_0"/"LABEL_1"
            #  * a descriptive name like "SAFE"/"PROMPT_INJECTION" (if
            #    id2label was set in config.json)
            # we'll normalize both cases.

            # first, assume numeric label encoded in the string
            label_num = None
            if label_str.startswith("LABEL_"):
                try:
                    label_num = int(label_str.split("_")[-1])
                except Exception:
                    label_num = None

            if label_num is None:
                # either we didn't parse a number, or the pipeline already
                # returned a descriptive name; look up in reverse map
                label_num = reverse_risk_map.get(label_str, 0)
                name = label_str
            else:
                name = risk_map.get(label_num, label_str)

            return {"label": label_num, "score": score, "name": name}
        else:
            return {"label": 0, "score": 0.0, "name": "SAFE", "error": "unexpected pipeline output"}
    except Exception as e:
        return {"label": 0, "score": 0.0, "name": "SAFE", "error": str(e)}