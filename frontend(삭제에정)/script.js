async function sendPrompt() {
    const prompt = document.getElementById("prompt").value;

    const response = await fetch("http://127.0.0.1:8000/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: prompt }),
    });

    const data = await response.json();
    document.getElementById("result").textContent = data.report;
}