from flask import Flask, request, jsonify
from flask_cors import CORS
from risk_engine import analyze_prompt
from risk_engine import ml_detector

app = Flask(__name__)

# Enable CORS for all routes
CORS(app)

@app.route("/analyze", methods=["POST"])
def analyze():

    data = request.json
    prompt = data.get("prompt", "")

    result = analyze_prompt(prompt)
    ml_result = ml_detector.predict(prompt)

    response = {
        "keywords": result["keywords"],
        "regex_matches": result["regex_matches"],
        "prompt_injection": result["prompt_injection"],
        "risk_score": result["risk_score"],
        "risk_level": result["risk_level"],
        "ml_prediction": ml_result
    }

    return jsonify(response)


if __name__ == "__main__":
    app.run(port=5000, debug=True)