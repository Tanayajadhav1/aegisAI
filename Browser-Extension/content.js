console.log("AegisAI - AI Prompt Firewall Loaded");
let COMPANY_ID = null

chrome.storage.local.get(["company_id"],(result)=>{

COMPANY_ID = result.company_id

console.log("Company ID:",COMPANY_ID)

})

const hostname = window.location.hostname;
console.log("Detected platform:", hostname);

let platform = "unknown";

if (hostname.includes("chat.openai.com") || hostname.includes("chatgpt.com")) {
    platform = "chatgpt";
}

else if (hostname.includes("perplexity.ai")) {
    platform = "perplexity";
}

else if (hostname.includes("copilot.microsoft.com") || hostname.includes("bing.com")) {
    platform = "copilot";
}

else if (hostname.includes("cursor.sh")) {
    platform = "cursor";
}

console.log("Platform identified as:", platform);
console.log("AI Prompt Firewall protecting:", platform);

const selectors = {

    chatgpt: {
        input: 'div[contenteditable="true"]',
        send: 'button[data-testid="send-button"]'
    },

    perplexity: {
        input: 'textarea',
        send: 'button[type="submit"]'
    },

    copilot: {
        input: 'textarea',
        send: 'button[type="submit"]'
    },

    cursor: {
        input: 'textarea',
        send: 'button[type="submit"]'
    }
};

/* Save original fetch */
const originalFetch = window.fetch;

/* -----------------------------
   Risk engine call
------------------------------*/
async function analyzePrompt(prompt) {

    const response = await originalFetch("http://localhost:5000/analyze", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            prompt,
            company_id: COMPANY_ID,
            platform
        })
    });

    return await response.json();
}

/* -----------------------------
   Risk popup
------------------------------*/
function showRiskPopup(result) {

    const popup = document.createElement("div");

    popup.style.position = "fixed";
    popup.style.top = "20px";
    popup.style.right = "20px";
    popup.style.background = "#ff4d4d";
    popup.style.color = "white";
    popup.style.padding = "15px";
    popup.style.borderRadius = "10px";
    popup.style.border = "2px solid #ffb3b3";

    popup.style.zIndex = "999999";

    popup.innerHTML = `
        <b>⚠ High Risk Prompt Detected</b><br>
        Risk Level: ${result.risk_level}<br>
        Risk Score: ${result.risk_score}
    `;

    document.body.appendChild(popup);

    setTimeout(() => popup.remove(), 5000);
}

/* -----------------------------
   Capture prompt from editor
------------------------------*/
function getPromptFromInput() {

    const selector = selectors[platform];

    if (!selector) return null;

    const input = document.querySelector(selector.input);

    if (!input) return null;

    if (input.tagName === "TEXTAREA") {
        return input.value.trim();
    }

    return input.innerText.trim();
}

/* -----------------------------
   SEND BUTTON INTERCEPTION
------------------------------*/
async function handleSendClick(event) {

    event.preventDefault();
    event.stopImmediatePropagation();

    const prompt = getPromptFromInput();

    if (!prompt) return;

    console.log("Prompt captured:", prompt);

    const result = await analyzePrompt(prompt);

    console.log("Risk result:", result);

    if (result.risk_level === "HIGH") {

        showRiskPopup(result);

        console.log("Prompt blocked due to HIGH risk");

        return;
    }

    console.log("Prompt safe, sending");

    const sendButton = document.querySelector(selectors[platform].send);

    if (sendButton) {
        sendButton.removeEventListener("click", handleSendClick, true);
        sendButton.click();
        sendButton.addEventListener("click", handleSendClick, true);
    }
}

async function handleEnterKey(event) {

    if (event.key !== "Enter" || event.shiftKey) return;

    event.preventDefault();
    event.stopImmediatePropagation();

    const prompt = getPromptFromInput();

    if (!prompt) return;

    console.log("Prompt captured (Enter):", prompt);

    const result = await analyzePrompt(prompt);

    console.log("Risk result:", result);

    if (result.risk_level === "HIGH") {

        showRiskPopup(result);

        console.log("Prompt blocked due to HIGH risk");

        return;
    }

    console.log("Prompt safe, sending");

    const sendButton = document.querySelector("button[data-testid='send-button']");
    if (sendButton) sendButton.click();
}

function attachEnterListener() {

    const selector = selectors[platform];

    if (!selector) return;

    const input = document.querySelector(selector.input);

    if (!input) return;

    if (!input.dataset.firewallEnterAttached) {

        input.dataset.firewallEnterAttached = "true";

        console.log("Enter listener attached");

        input.addEventListener("keydown", handleEnterKey, true);
    }
}

function attachButtonListener() {

    const selector = selectors[platform];

    if (!selector) return;

    const sendButton = document.querySelector(selector.send);

    if (!sendButton) return;

    if (!sendButton.dataset.firewallAttached) {

        console.log("Send button detected");

        sendButton.dataset.firewallAttached = "true";

        sendButton.addEventListener("click", handleSendClick, true);
    }
}

/* -----------------------------
   DOM observer (ChatGPT loads dynamically)
------------------------------*/
const observer = new MutationObserver(() => {
    attachButtonListener();
    attachEnterListener();
});

observer.observe(document.body, {
    childList: true,
    subtree: true
});

/* -----------------------------
   FETCH INTERCEPTION (backup)
------------------------------*/
window.fetch = async function (...args) {

    const url = args[0];
    const options = args[1];

    if (typeof url === "string" && url.includes("localhost:5000")) {
        return originalFetch.apply(this, args);
    }

    try {

        if (options && options.body) {

            const body = JSON.stringify(options.body);

            if (body.includes("messages")) {

                console.log("Possible AI request intercepted");

            }
        }

    } catch (err) {
        console.log("Fetch intercept error:", err);
    }

    return originalFetch.apply(this, args);
};