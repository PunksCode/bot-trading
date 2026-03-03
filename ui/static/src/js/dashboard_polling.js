/*async function fetchBotStatus() {
    try {
        const res = await fetch("/api/bot-status/");
        const data = await res.json();

        // Precio (simulado por ahora)
        if (data.price) {
            const priceEl = document.querySelector(".live-price");
            if (priceEl) priceEl.textContent = `$${data.price}`;
        }

        // Régimen
        if (data.regime && window.updateRegime) {
            window.updateRegime(data.regime);
        }

        console.log("📡 POLLING:", data);

        if (data.bot) {
            console.log("🤖 BOT:", data.bot);
        }

    } catch (err) {
        console.error("❌ Error polling:", err);
    }
}

setInterval(fetchBotStatus, 5000);*/
