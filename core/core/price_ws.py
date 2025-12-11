import os
import threading
from dotenv import load_dotenv
from django.core.cache import cache

load_dotenv()
SYMBOL = os.getenv("SYMBOL", "SOLUSDT").lower()

# Usamos el WebSocket oficial del conector
from binance.websocket.spot.websocket_stream import SpotWebsocketStreamClient as WSClient

_ws = None
_ws_thread = None
_started = False

def _on_message(_, message):
    # message es dict; para miniTicker viene en 'c' (close) como string
    # También soportamos 'ticker' normal
    try:
        if "c" in message:  # miniTicker: last price
            price = float(message["c"])
        elif "p" in message: # ticker: price change - no siempre trae last
            return
        else:
            return
        cache.set("last_price", price, timeout=60)  # 60s TTL
    except Exception:
        pass

def start_ws():
    global _ws, _ws_thread, _started
    if _started:
        return
    _started = True

    def run():
        global _ws
        _ws = WSClient(on_message=_on_message, ws_base_url="wss://testnet.binance.vision")
        # stream de miniTicker de un símbolo (rápido y liviano)
        _ws.mini_ticker(symbol=SYMBOL)
        # mantener el hilo vivo
        try:
            while _started:
                pass
        finally:
            try:
                _ws.stop()
            except Exception:
                pass

    _ws_thread = threading.Thread(target=run, daemon=True)
    _ws_thread.start()

def stop_ws():
    global _started, _ws
    _started = False
    try:
        if _ws:
            _ws.stop()
    except Exception:
        pass
