from risk_engine.analyzer import analyze_prompt
import json

p = (
    "Can you summarize these meeting notes from our internal strategy meeting? "
    "'Discussion topics: expanding the SaaS platform to Southeast Asia markets, "
    "increasing pricing tiers, and hiring 3 additional backend engineers for the "
    "Pune development office.'"
)

print(json.dumps(analyze_prompt(p), indent=2))
