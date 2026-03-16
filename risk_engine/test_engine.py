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
	
	# Show ML prediction details
	print("\n--- ML Prediction Details ---")
	print(f"Original ML Prediction:")
	print(f"  Label: {ml_result.get('label')} ({ml_result.get('name')})")
	print(f"  Confidence: {ml_result.get('score'):.4f}")
	
	if ml_result.get('zero_shot_triggered'):
		print(f"\nZero-Shot Layer 2 Analysis: TRIGGERED")
		zs = ml_result.get('zero_shot_analysis', {})
		print(f"  Intent Assessment: {zs.get('top_intent')}")
		print(f"  Intent Confidence: {zs.get('confidence', 0):.4f}")
		
		if ml_result.get('label_changed'):
			print(f"\n🔄 Label Corrected by Zero-Shot:")
			print(f"  Original: {ml_result.get('name')} → Final: {ml_result.get('final_name')}")
			print(f"  Reason: {ml_result.get('final_risk_reason', 'N/A')}")
		else:
			print(f"\n✓ Label Confirmed by Zero-Shot: {ml_result.get('final_name')}")
	else:
		print(f"\nZero-Shot Layer 2 Analysis: SKIPPED")
	
	print(f"\n--- FINAL RISK ASSESSMENT ---")
	print(f"Risk Score: {result['risk_score']}")
	print(f"Risk Level: {result['risk_level']}")


if __name__ == "__main__":
	main()