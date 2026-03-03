/*const socket = new WebSocket(
    (location.protocol === "https:" ? "wss://" : "ws://") +
    window.location.host +
    "/ws/dashboard/"
);

socket.onmessage = (e) => {
    const data = JSON.parse(e.data);

    if (data.price) {
        const priceEl = document.querySelector(".header__price");
        if (priceEl) {
            priceEl.textContent = `$${data.price}`;
        }
    }

    if (data.regime && window.updateRegime) {
        window.updateRegime(data.regime);
    }

    console.log("📡 WS DATA:", data);
};*/
