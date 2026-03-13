const container = document.getElementById("promptList");

chrome.storage.local.get(["prompts"], function (result) {

  let prompts = result.prompts || [];

  if (prompts.length === 0) {
    container.innerHTML = "No prompts captured.";
    return;
  }

  prompts.reverse().forEach(p => {

    const div = document.createElement("div");

    div.className = "prompt";

    div.innerHTML = `
      <b>Platform:</b> ${p.platform}<br>
      <b>Prompt:</b> ${p.prompt}
    `;

    container.appendChild(div);

  });

});