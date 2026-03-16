from flask import Flask, request, jsonify
from flask_cors import CORS
from risk_engine import analyze_prompt
from risk_engine import ml_detector

import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

app = Flask(__name__)

# Enable CORS
CORS(app)

# -----------------------------
# Firebase Initialization
# -----------------------------
cred = credentials.Certificate("firebase_key.json")
firebase_admin.initialize_app(cred)

db = firestore.client()


# -----------------------------
# Save violation to Firestore
# -----------------------------
def get_client_ip():
    # Handles proxies / load balancers
    if request.headers.get("X-Forwarded-For"):
        ip = request.headers.get("X-Forwarded-For").split(",")[0]
    else:
        ip = request.remote_addr
    return ip


def save_violation(prompt, result, ml_result):

    client_ip = get_client_ip()

    violation = {
        "prompt": prompt,
        "risk_score": result.get("risk_score", 0),
        "severity": result.get("risk_level", "LOW"),
        "prompt_injection": result.get("prompt_injection", False),
        "ml_prediction": ml_result,
        "keywords": result.get("keywords", []),
        "regex_matches": result.get("regex_matches", []),
        "time": datetime.utcnow(),
        "platform": request.headers.get("Origin", "unknown"),
        "user": client_ip   # 👈 store IP here
    }

    db.collection("violations").add(violation)

    print("Violation saved to Firestore | IP:", client_ip)

# -----------------------------
# Analyze Prompt Endpoint
# -----------------------------
@app.route("/analyze", methods=["POST"])
def analyze():

    data = request.get_json(silent=True) or {}
    prompt = data.get("prompt", "")

    print("Prompt received:", prompt)

    # Run rule engine
    result = analyze_prompt(prompt)

    # Run ML detector
    try:
        ml_result = ml_detector.predict([prompt])[0]
    except Exception:
        ml_result = "unknown"

    # Save HIGH risk prompts
    if result.get("risk_level") == "HIGH":
        save_violation(prompt, result, ml_result)

    response = {
        "keywords": result.get("keywords", []),
        "regex_matches": result.get("regex_matches", []),
        "prompt_injection": result.get("prompt_injection", False),
        "risk_score": result.get("risk_score", 0),
        "risk_level": result.get("risk_level", "LOW"),
        "ml_prediction": ml_result
    }

    return jsonify(response)


# -----------------------------
# Run server
# -----------------------------
if __name__ == "__main__":
    app.run(port=5000, debug=True)