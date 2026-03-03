document.addEventListener('DOMContentLoaded', function() {
    
    // ------------------------------------------
    // 1. MATRIX BINARIO (Solo 0 y 1)
    // ------------------------------------------
    const canvas = document.getElementById('matrix-bg');
    const ctx = canvas.getContext('2d');

    // Ajustar al tamaño completo
    const resizeCanvas = () => {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
    };
    window.addEventListener('resize', resizeCanvas);
    resizeCanvas();

    // Configuración binaria
    const binary = "01"; // <--- SOLO ESTO
    const fontSize = 14;
    const columns = canvas.width / fontSize;

    const drops = [];
    for(let x = 0; x < columns; x++) drops[x] = 1;

    const draw = () => {
        // Estela muy transparente para que no sea muy invasivo
        ctx.fillStyle = 'rgba(9, 10, 15, 0.05)'; 
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        ctx.fillStyle = '#0F0'; // Verde Matrix Clásico
        ctx.font = fontSize + 'px monospace';

        for(let i = 0; i < drops.length; i++) {
            const text = binary.charAt(Math.floor(Math.random() * binary.length));
            
            // Opacidad aleatoria para dar profundidad
            ctx.globalAlpha = Math.random() * 0.5 + 0.1; 
            
            ctx.fillText(text, i*fontSize, drops[i]*fontSize);

            if(drops[i]*fontSize > canvas.height && Math.random() > 0.975) {
                drops[i] = 0;
            }
            drops[i]++;
        }
        ctx.globalAlpha = 1.0; // Reset opacidad
    };
    setInterval(draw, 50); // Un poco más lento para no marear

    // ------------------------------------------
    // 2. TRADINGVIEW WIDGET (Profesional)
    // ------------------------------------------
    if (document.getElementById('tradingview_widget')) {
        new TradingView.widget({
            "autosize": true,
            "symbol": "BINANCE:BTCUSDT",
            "interval": "60",
            "timezone": "Etc/UTC",
            "theme": "dark",
            "style": "1",
            "locale": "es",
            "toolbar_bg": "#f1f3f6",
            "enable_publishing": false,
            "hide_top_toolbar": false,
            "save_image": false,
            "container_id": "tradingview_widget",
            "overrides": {
                "paneProperties.background": "#141923", // Coincide con el Glass-bg
                "paneProperties.vertGridProperties.color": "rgba(255,255,255,0.05)",
                "paneProperties.horzGridProperties.color": "rgba(255,255,255,0.05)",
                "scalesProperties.textColor": "#94a3b8"
            }
        });
    }

    // ------------------------------------------
    // 3. CHART.JS (Limpio y Suave)
    // ------------------------------------------
    const bridge = document.getElementById('data-bridge');
    if (bridge) {
        const data = JSON.parse(bridge.textContent);
        const ctxChart = document.getElementById('equityChart').getContext('2d');
        
        // Gradiente azul profesional
        const gradient = ctxChart.createLinearGradient(0, 0, 0, 300);
        gradient.addColorStop(0, 'rgba(59, 130, 246, 0.3)');
        gradient.addColorStop(1, 'rgba(59, 130, 246, 0.0)');

        new Chart(ctxChart, {
            type: 'line',
            data: {
                labels: data.labels,
                datasets: [{
                    label: 'Equity',
                    data: data.data,
                    borderColor: '#3b82f6', // Azul Enterprise
                    backgroundColor: gradient,
                    borderWidth: 2,
                    pointRadius: 0,
                    pointHoverRadius: 4,
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    x: { display: false },
                    y: { 
                        display: true,
                        grid: { color: 'rgba(255,255,255,0.05)' },
                        ticks: { color: '#64748b', font: {size: 10} }
                    }
                }
            }
        });
    }
});