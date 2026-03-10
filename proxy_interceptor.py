"""
AegisAI - Network Prompt Interceptor
RUN:     python proxy_interceptor.py
BROWSER: Set proxy to 127.0.0.1:8080  then visit http://mitm.it
"""

import json
import requests
import logging
import sys
import io
import re
from datetime import datetime
from mitmproxy import http
from mitmproxy.tools.main import mitmdump

logging.disable(logging.CRITICAL)

BACKEND_URL = "http://127.0.0.1:8000/analyze"
PROXY_PORT  = 8080

# ── These hosts we NEVER want, regardless of path ────────────
SKIP_HOSTS = [
    "grammarly.com", "quillbot.com", "amplitude.com", "datadoghq.com",
    "intercom.io", "s-microsoft.com", "android.clients",
    "s-cdn.anthropic.com", "xboxlive.com",
]

# ── Analytics/telemetry paths to always skip ─────────────────
SKIP_PATHS = [
    "/v1/t", "/v1/p", "/sentry", "/amplitude", "/segment", "/beacon",
    "/collect", "/telemetry", "/uma/v2", "/ukm", "/batch/import",
    "/OneCollec", "/domainreliability", "/api/v2/rum", "/api/v2/logs",
    "/com.quillbot", "/fpws", "/pubsub", "/register3", "/chrome-sync",
    "/messenger/web", "/web/metrics", "/event_logging", "/title",
    "/optimizationguide", "/c2dm", "/update2", "/clientservices",
    "/chrome-variations", "/log", "/gen_204",
]

# ── Non-AI google subdomains to skip ─────────────────────────
SKIP_GOOGLE_HOSTS = [
    "update.googleapis.com", "clientservices.googleapis.com",
    "clients4.google.com", "clients1.google.com",
    "optimizationguide-pa.googleapis.com",
    "android.clients.google.com", "play.googleapis.com",
    "fonts.googleapis.com", "accounts.google.com",
]

# ── Non-AI microsoft subdomains to skip ──────────────────────
SKIP_MICROSOFT_HOSTS = [
    "mobile.events.data.microsoft.com",
    "settings-win.data.microsoft.com",
    "browser.events.data.microsoft.com",
]

AI_TARGETS = {
    "ChatGPT": {
        "hosts": ["api.openai.com", "chatgpt.com", "chat.openai.com"],
        "paths": [
            "/v1/chat/completions",
            "/backend-api/conversation",
            "/backend-anon/conversation",
        ],
        "extractor": "openai",
    },
    "Claude": {
        "hosts": ["claude.ai", "api.anthropic.com", "a-api.anthropic.com"],
        "paths": [
            "/v1/messages", "/v1/m", "/api/append_message",
            "/completion", "/api/organizations",
        ],
        "extractor": "anthropic",
    },
    "Gemini": {
        "hosts": [
            "gemini.google.com",
            "generativelanguage.googleapis.com",
            "aistudio.google.com",
        ],
        "paths": [
            "/_/BardChatUi", "/BardChatUi", "/assistant.lamda",
            "/v1beta/models", "/v1/models", "/api/generate",
        ],
        "extractor": "gemini",
    },
    "Perplexity": {
        "hosts": ["www.perplexity.ai", "perplexity.ai"],
        "paths": ["/rest/sse", "/api/ask", "/socket.io", "/api/search"],
        "extractor": "perplexity",
    },
    "Copilot": {
        "hosts": [
            "copilot.microsoft.com",
            "sydney.bing.com",
            "edgeservices.bing.com",
            "www.bing.com",
        ],
        "paths": [
            "/c/api/chat",
            "/turing/conversation/chats",
            "/turing/conversation/create",
        ],
        "extractor": "copilot",
    },
}

# ── WEBSOCKET HOST ROUTING ────────────────────────────────────
# Maps host substrings → (platform, extractor_key)
WEBSOCKET_PLATFORMS = {
    "anthropic.com": ("Claude",      "anthropic"),
    "claude.ai":     ("Claude",      "anthropic"),
    "perplexity.ai": ("Perplexity",  "perplexity"),
    "sydney.bing":   ("Copilot",     "copilot"),        # FIX: was missing
    "bing.com":      ("Copilot",     "copilot"),        # FIX: was missing
    "chatgpt.com":   ("ChatGPT",     "openai"),         # FIX: was missing
    "openai.com":    ("ChatGPT",     "openai"),         # FIX: was missing
}

# ── EXTRACTORS ───────────────────────────────────────────────

def extract_openai(body):
    for msg in reversed(body.get("messages", [])):
        role = msg.get("role") or (msg.get("author") or {}).get("role", "")
        if role == "user":
            c = msg.get("content", "")
            if isinstance(c, dict):
                parts = c.get("parts", [])
                return " ".join(str(p) for p in parts if isinstance(p, str))
            if isinstance(c, list):
                return " ".join(p.get("text","") for p in c if p.get("type")=="text")
            if isinstance(c, str) and c.strip():
                return c
    return None

def extract_anthropic(body):
    for msg in reversed(body.get("messages", [])):
        if msg.get("role") == "user":
            c = msg.get("content", "")
            if isinstance(c, list):
                return " ".join(p.get("text","") for p in c if p.get("type")=="text")
            if isinstance(c, str) and c.strip():
                return c
    for key in ("prompt", "text", "initial_text", "query", "input"):
        if body.get(key) and str(body[key]).strip():
            return str(body[key])
    if body.get("human_turn", {}).get("text"):
        return body["human_turn"]["text"]
    return None

def extract_gemini(body):
    # Standard REST API format (generativelanguage.googleapis.com)
    try:
        parts = body["contents"][-1]["parts"]
        return " ".join(p.get("text","") for p in parts if "text" in p)
    except (KeyError, IndexError, TypeError):
        pass

    # FIX: Gemini web UI sends nested protobuf-like lists via BardChatUi
    # The user message is typically buried in body[0][0] or body[1][0][0]
    if isinstance(body, list):
        # Try common positions in the nested array structure
        candidates = []
        try: candidates.append(str(body[0][0]))
        except: pass
        try: candidates.append(str(body[1][0][0]))
        except: pass
        try: candidates.append(str(body[0][0][0]))
        except: pass
        for c in candidates:
            if c and len(c) > 3 and c not in ("None", "[]"):
                return c

    return body.get("inputText") or body.get("prompt") or body.get("query") or None

def extract_gemini_wrb(raw_text):
    """
    FIX: Gemini web UI (/_/BardChatUi/data/listen) uses a WRB (Web Request Bundler)
    format — not JSON. The user prompt is encoded as a JSON string within the response.
    We extract it with a targeted regex.
    """
    # The prompt appears as a plain string inside the wrb payload
    # Pattern: find quoted strings that look like user messages (>10 chars, not a URL/token)
    matches = re.findall(r'"([^"\\]{10,})"', raw_text)
    for m in matches:
        # Skip obvious non-prompt strings (URLs, tokens, single words)
        if " " in m and not m.startswith("http") and len(m) < 2000:
            return m
    return None

def extract_perplexity(body):
    return (body.get("query") or body.get("search_focus") or
            body.get("text_input") or body.get("q") or None)

def extract_copilot(body):
    # FIX: Copilot WebSocket sends messages as JSON with a "text" field
    # and also uses a "arguments" list structure in newer versions
    try:
        for msg in reversed(body.get("messages", [])):
            author = msg.get("author") or msg.get("role", "")
            if author == "user":
                text = msg.get("text","") or msg.get("content","")
                if text and text.strip():
                    return text
    except (KeyError, TypeError):
        pass

    # FIX: Newer Copilot format uses arguments[0].messages
    try:
        for arg in body.get("arguments", []):
            for msg in reversed(arg.get("messages", [])):
                if msg.get("author") == "user":
                    text = msg.get("text","") or msg.get("content","")
                    if text and text.strip():
                        return text
    except (KeyError, TypeError):
        pass

    return body.get("text") or body.get("query") or body.get("userMessage") or None

EXTRACTORS = {
    "openai": extract_openai, "anthropic": extract_anthropic,
    "gemini": extract_gemini, "perplexity": extract_perplexity,
    "copilot": extract_copilot,
}

# ── HELPERS ──────────────────────────────────────────────────

def should_skip(host, path):
    h = host.lower()
    p = path.lower()
    if any(b in h for b in SKIP_HOSTS):           return True
    if any(b in h for b in SKIP_GOOGLE_HOSTS):    return True
    if any(b in h for b in SKIP_MICROSOFT_HOSTS): return True
    if any(s in p for s in SKIP_PATHS):           return True
    return False

def match_platform(host, path):
    h, p = host.lower(), path.lower()
    for name, cfg in AI_TARGETS.items():
        if any(x in h for x in cfg["hosts"]):
            if any(x in p for x in cfg["paths"]):
                return name, cfg["extractor"]
    return None, None

def safe_json(flow):
    try: return json.loads(flow.request.content)
    except: return None

def safe_json_from_bytes(data):
    """FIX: Parse JSON from raw bytes (for WebSocket messages and SSE chunks)."""
    try:
        if isinstance(data, (bytes, bytearray)):
            data = data.decode("utf-8", errors="ignore")
        # Strip SSE prefix if present: "data: {...}"
        if data.startswith("data:"):
            data = data[5:].strip()
        return json.loads(data)
    except:
        return None

def out(msg):
    try:
        sys.__stdout__.write(msg)
        sys.__stdout__.flush()
    except Exception:
        pass

def print_capture(platform, prompt, host, path):
    ts  = datetime.now().strftime("%H:%M:%S")
    bar = "=" * 64
    out(f"\n{bar}\n")
    out(f"[{ts}] AegisAI — Prompt Captured\n")
    out(f"  Platform : {platform}\n")
    out(f"  Endpoint : {host}{path[:80]}\n")
    out(f"  Prompt   : {prompt[:500]}{'...' if len(prompt)>500 else ''}\n")
    out(f"{bar}\n")

def send_to_backend(platform, prompt):
    try:
        s = requests.Session()
        s.trust_env = False
        r = s.post(BACKEND_URL, json={"prompt": prompt, "platform": platform}, timeout=5)
        res = r.json()
        out(f"  Risk: {res.get('risk_score','N/A')}/100 ({res.get('risk_level','N/A')})  "
            f"Action: {res.get('action','N/A')}  "
            f"Keywords: {res.get('keywords_found',[])}\n\n")
    except requests.exceptions.ConnectionError:
        out("  [!] Backend offline — run: uvicorn risk_engine.analyzer:app --port 8000\n\n")
    except Exception as e:
        out(f"  [!] Backend error: {e}\n\n")

# ── DEBUG: set to the platform you want to find endpoints for ─
# Options: "ChatGPT" | "Gemini" | "Perplexity" | "Copilot" | None
DEBUG_PLATFORM = None

DEBUG_HOSTS = {
    "ChatGPT":    ["openai.com", "chatgpt.com"],
    "Gemini":     ["gemini.google.com", "bard.google.com", "generativelanguage"],
    "Perplexity": ["perplexity.ai"],
    "Copilot":    ["copilot.microsoft.com", "bing.com", "sydney.bing"],
}

# ── ADDON ────────────────────────────────────────────────────

class AegisAIInterceptor:

    def request(self, flow: http.HTTPFlow):
        host   = flow.request.pretty_host
        path   = flow.request.path
        method = flow.request.method

        # ── Debug mode: show all POSTs for one platform ──────
        if DEBUG_PLATFORM and method in ("POST","PUT","PATCH"):
            watch = DEBUG_HOSTS.get(DEBUG_PLATFORM, [])
            if any(w in host.lower() for w in watch):
                body = safe_json(flow)
                preview = json.dumps(body)[:300] if body else flow.request.content[:300].decode("utf-8","ignore")
                out(f"[DEBUG {DEBUG_PLATFORM}] POST {host}{path}\n")
                out(f"  Body: {preview}\n\n")

        if should_skip(host, path):              return
        if method not in ("POST","PUT","PATCH"): return

        platform, extractor_key = match_platform(host, path)
        if platform is None:                     return

        # ── FIX: Gemini WRB format (/_/BardChatUi/data/listen) ──
        # This endpoint sends urlencoded form data, not JSON.
        # The actual payload is in the "f.req" form field.
        if platform == "Gemini" and "BardChatUi" in path:
            try:
                content_type = flow.request.headers.get("content-type", "")
                if "application/x-www-form-urlencoded" in content_type:
                    from urllib.parse import parse_qs, unquote
                    raw = flow.request.content.decode("utf-8", errors="ignore")
                    params = parse_qs(raw)
                    freq = params.get("f.req", [""])[0]
                    if freq:
                        # f.req is a JSON-encoded string containing nested arrays
                        outer = json.loads(freq)
                        # The inner payload is a JSON string at outer[3]
                        inner_str = outer[3] if len(outer) > 3 else None
                        if inner_str:
                            inner = json.loads(inner_str)
                            prompt = extract_gemini(inner)
                            if not prompt:
                                prompt = extract_gemini_wrb(inner_str)
                        else:
                            prompt = extract_gemini_wrb(freq)
                        if prompt and prompt.strip():
                            print_capture(platform, prompt, host, path)
                            send_to_backend(platform, prompt)
                            return
            except Exception:
                pass

        # ── FIX: ChatGPT SSE streaming — body may be empty at request time.
        # We attempt JSON parse; if empty we fall through silently.
        # The `response` hook below handles the streamed reply for confirmation,
        # but the outgoing request body still contains the full message list.
        body         = safe_json(flow)
        extractor_fn = EXTRACTORS.get(extractor_key)
        prompt       = extractor_fn(body) if (extractor_fn and body) else None

        if not prompt or not prompt.strip():     return

        print_capture(platform, prompt, host, path)
        send_to_backend(platform, prompt)

    def websocket_message(self, flow: http.HTTPFlow):
        """
        FIX: Extended to cover Copilot (sydney.bing.com) and ChatGPT WebSocket,
        in addition to the original Claude and Perplexity support.
        """
        host = flow.request.pretty_host
        h    = host.lower()

        # Resolve platform from host
        platform, extractor_key = None, None
        for host_fragment, (plat, ext_key) in WEBSOCKET_PLATFORMS.items():
            if host_fragment in h:
                platform, extractor_key = plat, ext_key
                break

        if platform is None:
            return

        msg = flow.websocket.messages[-1]
        if not msg.from_client:
            return

        # FIX: Copilot sends a delimited format: multiple JSON objects separated
        # by the record separator character (\x1e). Split and try each.
        raw_content = msg.content
        if isinstance(raw_content, (bytes, bytearray)):
            raw_content = raw_content.decode("utf-8", errors="ignore")

        # Try record-separator split (Copilot SignalR protocol)
        chunks = raw_content.split("\x1e") if "\x1e" in raw_content else [raw_content]

        extractor_fn = EXTRACTORS.get(extractor_key)

        for chunk in chunks:
            chunk = chunk.strip()
            if not chunk:
                continue
            try:
                data   = json.loads(chunk)
                prompt = extractor_fn(data) if extractor_fn else None
                if prompt and prompt.strip():
                    print_capture(platform, prompt, host, "/websocket")
                    send_to_backend(platform, prompt)
                    return  # Only report first prompt found per message
            except Exception:
                continue

addons = [AegisAIInterceptor()]

if __name__ == "__main__":
    sys.__stdout__.write("\n")
    sys.__stdout__.write("╔══════════════════════════════════════════════╗\n")
    sys.__stdout__.write("║        AegisAI - Network Interceptor         ║\n")
    sys.__stdout__.write("║   Monitoring: ChatGPT | Claude | Gemini      ║\n")
    sys.__stdout__.write("║              Perplexity | Copilot            ║\n")
    sys.__stdout__.write(f"║   Proxy running on  127.0.0.1:{PROXY_PORT}          ║\n")
    sys.__stdout__.write("╚══════════════════════════════════════════════╝\n")
    sys.__stdout__.write("  Browser proxy : 127.0.0.1:8080\n")
    sys.__stdout__.write("  CA cert       : http://mitm.it\n\n")
    if DEBUG_PLATFORM:
        sys.__stdout__.write(f"  DEBUG MODE : watching {DEBUG_PLATFORM} traffic\n\n")
    sys.__stdout__.write("  Waiting for prompts...\n\n")
    sys.__stdout__.flush()

    sys.stdout = io.StringIO()

    sys.argv = [
        "mitmdump",
        "--listen-port", str(PROXY_PORT),
        "--scripts",     __file__,
        "--ssl-insecure",
        "--quiet",
        "--set", "termlog_verbosity=error",
        "--set", "flow_detail=0",
    ]
    mitmdump()