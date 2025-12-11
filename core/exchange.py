import os
from binance.spot import Spot as Client
from dotenv import load_dotenv

load_dotenv(override=True, encoding="utf-8")

API_KEY = os.getenv("BINANCE_API_KEY")
API_SECRET = os.getenv("BINANCE_API_SECRET")
BASE_URL = os.getenv("BINANCE_BASE_URL", "https://testnet.binance.vision")

def _client():
    if not API_KEY or not API_SECRET:
        raise RuntimeError("Faltan claves en .env (BINANCE_API_KEY / BINANCE_API_SECRET).")
    return Client(api_key=API_KEY, api_secret=API_SECRET, base_url=BASE_URL)

def ping() -> bool:
    try:
        _client().ping()
        return True
    except Exception:
        return False

def get_price(symbol: str) -> float:
    data = _client().ticker_price(symbol)
    return float(data["price"])

def market_order(symbol: str, side: str, quantity: float):
    return _client().new_order(symbol=symbol, side=side, type="MARKET", quantity=quantity)
