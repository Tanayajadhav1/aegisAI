from keyword_detector import detect_keywords
from regex_detector import detect_regex
from prompt_injection_detector import detect_prompt_injection
from risk_scoring import calculate_risk

prompt = input("Enter prompt: ")

keyword_hits = detect_keywords(prompt)
regex_hits = detect_regex(prompt)
injection_hits = detect_prompt_injection(prompt)

score, level = calculate_risk(keyword_hits, regex_hits, injection_hits)

print("\n--- Detection Results ---")
print("Keywords detected:", keyword_hits)
print("Regex matches:", regex_hits)
print("Prompt injection:", injection_hits)

print("\nRisk Score:", score)
print("Risk Level:", level)