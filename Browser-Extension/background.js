console.log("Background script running");

chrome.runtime.onMessage.addListener((message, sender) => {

  if (message.type === "PROMPT_CAPTURED") {

    console.log("Prompt received:", message.prompt);

    chrome.storage.local.get(["prompts"], function (result) {

      let prompts = result.prompts || [];

      prompts.push(message);

      chrome.storage.local.set({ prompts: prompts });

    });

  }

});