from risk_engine import analyze_prompt
from risk_engine import ml_detector

def main():
	prompt = input("Enter prompt: ")
	result = analyze_prompt(prompt)
	ml_result = ml_detector.predict(prompt)

	print("\n--- Detection Results ---")
	print("Keywords detected:", result["keywords"])
	print("Regex matches:", result["regex_matches"])
	print("Prompt injection:", result["prompt_injection"])
	print("ML Prediction:", ml_result)

	print("\nRisk Score:", result["risk_score"])
	print("Risk Level:", result["risk_level"])


if __name__ == "__main__":
	main()