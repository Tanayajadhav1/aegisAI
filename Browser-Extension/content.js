console.log("AI Prompt Firewall Loaded");

const platform = window.location.hostname;
console.log("Detected platform:", platform);

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
        body: JSON.stringify({ prompt })
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

    const input = document.querySelector('div[contenteditable="true"]');

    if (!input) return null;

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

    const sendButton = document.querySelector("button[data-testid='send-button']");

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

    const input = document.querySelector('div[contenteditable="true"]');

    if (!input) return;

    if (!input.dataset.firewallEnterAttached) {

        input.dataset.firewallEnterAttached = "true";

        console.log("Enter listener attached");

        input.addEventListener("keydown", handleEnterKey, true);
    }
}

function attachButtonListener() {

    const sendButton = document.querySelector("button[data-testid='send-button']");

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