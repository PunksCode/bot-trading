import os
from dotenv import load_dotenv
from .exchange import market_order, get_price

load_dotenv()
SYMBOL = os.getenv("SYMBOL", "SOLUSDT")

def execute_signal(symbol, signal, qty):
    if signal not in ("BUY", "SELL"):
        return {"status": "SKIP", "reason": "HOLD"}
    price = get_price(symbol)
    try:
        order = market_order(symbol, signal, qty)
        return {"status": "OK", "order_id": order.get("orderId"), "price": price}
    except Exception as e:
        return {"status": "ERROR", "error": str(e), "price": price}
