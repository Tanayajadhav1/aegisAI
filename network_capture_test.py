"""
AegisAI – Public Network Test (No MITM needed)
================================================
Tests the SAME detection logic without a proxy.
Simulates prompts as if they were captured from the network.

Use this on your personal device / public Wi-Fi to verify
keyword detection + risk scoring works before deploying the proxy.

RUN:
    python network_capture_test.py

WHAT IT DOES:
    - Sends 10 realistic test prompts (safe + dangerous) to your FastAPI backend
    - Prints a colour-coded risk report in terminal
    - Does NOT need mitmproxy or special network access

REQUIREMENTS:
    pip install requests colorama
    Your FastAPI backend must be running:  uvicorn main:app --reload
"""

import requests
import json
import time
from datetime import datetime

try:
    from colorama import Fore, Style, init
    init(autoreset=True)
except ImportError:
    class Fore:
        RED = GREEN = YELLOW = CYAN = MAGENTA = WHITE = ""
    class Style:
        BRIGHT = RESET_ALL = ""

# ──────────────────────────────────────────────
BACKEND_URL = "http://127.0.0.1:8000/analyze"
# ──────────────────────────────────────────────

TEST_CASES = [
    # (platform, prompt, expected_risk)
    ("ChatGPT",    "What is the capital of France?",                                  "LOW"),
    ("Gemini",     "Write a poem about mountains.",                                   "LOW"),
    ("Claude",     "Explain quantum computing in simple terms.",                      "LOW"),
    ("Perplexity", "My password is Admin@1234. How do I reset it?",                  "HIGH"),
    ("ChatGPT",    "Here is our api key: sk-abc123secret. Can you use it?",           "HIGH"),
    ("Copilot",    "The confidential merger deal is with CompanyX for $5M.",          "HIGH"),
    ("Claude",     "My private key: -----BEGIN RSA PRIVATE KEY-----\nMIIE...",        "HIGH"),
    ("Gemini",     "Summarize this internal data: Q3 revenue was $2.3M.",             "HIGH"),
    ("Perplexity", "How does photosynthesis work?",                                   "LOW"),
    ("ChatGPT",    "The secret project codename is FALCON. Don't share externally.",  "HIGH"),
]


def send_prompt(platform: str, prompt: str) -> dict:
    try:
        resp = requests.post(
            BACKEND_URL,
            json={"prompt": prompt, "platform": platform},
            timeout=5
        )
        return resp.json()
    except requests.exceptions.ConnectionError:
        # Backend not running – use local keyword detection as fallback
        return local_fallback(prompt)
    except Exception as e:
        return {"error": str(e)}


def local_fallback(prompt: str) -> dict:
    """Minimal local detection if backend is offline."""
    SENSITIVE = ["password", "api key", "secret", "confidential",
                 "internal data", "private key", "token", "credential"]
    hits = [k for k in SENSITIVE if k in prompt.lower()]
    score = min(len(hits) * 25, 100)
    return {
        "risk_score":     score,
        "keywords_found": hits,
        "action":         "BLOCK" if score >= 50 else "ALLOW",
        "source":         "local_fallback"
    }


def colour_risk(score):
    if score is None:
        return f"{Fore.WHITE}N/A"
    if score >= 70:
        return f"{Fore.RED}{Style.BRIGHT}{score}"
    if score >= 40:
        return f"{Fore.YELLOW}{score}"
    return f"{Fore.GREEN}{score}"


def run_tests():
    print(f"\n{Fore.CYAN}{Style.BRIGHT}{'═'*65}")
    print(f"   AegisAI – Public Network Simulation Test")
    print(f"   Backend : {BACKEND_URL}")
    print(f"   Time    : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'═'*65}{Style.RESET_ALL}\n")

    passed = failed = 0

    for i, (platform, prompt, expected) in enumerate(TEST_CASES, 1):
        print(f"{Fore.CYAN}[{i:02d}] Platform : {platform}")
        print(f"     Prompt   : {prompt[:80]}{'...' if len(prompt)>80 else ''}")

        result = send_prompt(platform, prompt)

        if "error" in result:
            print(f"     {Fore.RED}ERROR: {result['error']}\n")
            failed += 1
            continue

        score    = result.get("risk_score", 0)
        keywords = result.get("keywords_found", [])
        action   = result.get("action", "UNKNOWN")
        source   = result.get("source", "backend")

        actual_risk = "HIGH" if score >= 50 else "LOW"
        match = actual_risk == expected

        status_icon  = f"{Fore.GREEN}✔" if match else f"{Fore.RED}✘"
        action_colour = Fore.RED if action == "BLOCK" else Fore.GREEN

        print(f"     Risk     : {colour_risk(score)}/100  |  Action: {action_colour}{action}")
        print(f"     Keywords : {Fore.MAGENTA}{keywords if keywords else 'none'}")
        print(f"     Source   : {Fore.WHITE}{source}  |  Expected: {expected}  {status_icon}")
        print()

        if match:
            passed += 1
        else:
            failed += 1

        time.sleep(0.2)   # slight delay so you can read the output

    # ── Summary ──
    total = passed + failed
    pct   = int(passed / total * 100) if total else 0
    print(f"{Fore.CYAN}{'═'*65}")
    print(f"  Results : {Fore.GREEN}{passed} passed  {Fore.RED}{failed} failed  {Fore.WHITE}({pct}% accuracy)")
    print(f"{Fore.CYAN}{'═'*65}\n")

    print(f"{Style.BRIGHT}Next step → run the MITM proxy on your private network:")
    print(f"  python proxy_interceptor.py")
    print(f"  Then set browser proxy to 127.0.0.1:8080 and visit http://mitm.it\n")


if __name__ == "__main__":
    run_tests()