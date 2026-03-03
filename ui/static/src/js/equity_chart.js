document.addEventListener("DOMContentLoaded", () => {

    const bridge = document.getElementById('chart-data-bridge');
    if (!bridge) return;

    let data;
    try {
        data = JSON.parse(bridge.textContent);
    } catch (e) {
        return;
    }

    const fechas = data.fechas;
    const equityValues = data.equityValues;

    const canvas = document.getElementById('pnlChart');
    if (!canvas) return;

    const ctx = canvas.getContext('2d');

    // Gradiente azul corporativo
    const gradient = ctx.createLinearGradient(0, 0, 0, canvas.height || 300);
    gradient.addColorStop(0, 'rgba(59, 130, 246, 0.25)'); // Blue con transparencia
    gradient.addColorStop(1, 'rgba(59, 130, 246, 0.0)');  // Transparente

    new Chart(ctx, {
        type: 'line',
        data: {
            labels: fechas,
            datasets: [{
                label: 'Equity (USDT)',
                data: equityValues,
                borderColor: '#3B82F6', // Azul Accent
                backgroundColor: gradient,
                borderWidth: 2,
                pointRadius: 0,
                pointHoverRadius: 5,
                pointBackgroundColor: '#FFFFFF',
                fill: true,
                tension: 0.3
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: 'index',
                intersect: false,
            },
            plugins: {
                legend: { display: false },
                tooltip: {
                    backgroundColor: '#0E1116',
                    titleColor: '#8B949E',
                    bodyColor: '#FFFFFF',
                    borderColor: '#1A2028',
                    borderWidth: 1,
                    padding: 12,
                    displayColors: false,
                    callbacks: {
                        label: function (context) {
                            return '$ ' + context.parsed.y.toFixed(2);
                        }
                    }
                }
            },
            scales: {
                x: {
                    grid: { display: false },
                    ticks: {
                        color: '#535C68',
                        maxTicksLimit: 6,
                        maxRotation: 0
                    }
                },
                y: {
                    grid: {
                        color: 'rgba(255,255,255,0.03)',
                        borderDash: [5, 5]
                    },
                    ticks: {
                        color: '#535C68',
                        callback: function (value) { return '$' + value; }
                    },
                    beginAtZero: false
                }
            }
        }
    });
});