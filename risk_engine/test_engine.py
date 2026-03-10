from risk_engine import analyze_prompt


def main():
	prompt = input("Enter prompt: ")
	result = analyze_prompt(prompt)

	print("\n--- Detection Results ---")
	print("Keywords detected:", result["keywords"])
	print("Regex matches:", result["regex_matches"])
	print("Prompt injection:", result["prompt_injection"])

	print("\nRisk Score:", result["risk_score"])
	print("Risk Level:", result["risk_level"])


if __name__ == "__main__":
	main()