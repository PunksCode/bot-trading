document.addEventListener("DOMContentLoaded", () => {
        new TradingView.widget({
            "autosize": true,
            "symbol": "BINANCE:BTCUSDT",
            "interval": "60",
            "timezone": "America/Argentina/Buenos_Aires",
            "theme": "dark",
            "style": "1",
            "locale": "es",
            "toolbar_bg": "#0E1116",
            "enable_publishing": false,
            "hide_top_toolbar": false,
            "container_id": "tradingview_widget",
            "overrides": {
                "paneProperties.background": "#0E1116",
                "paneProperties.vertGridProperties.color": "rgba(255,255,255,0.03)",
                "paneProperties.horzGridProperties.color": "rgba(255,255,255,0.03)",
                "scalesProperties.textColor": "#8B949E"
            }
        });
});