import os
from binance.spot import Spot as Client
from dotenv import load_dotenv

load_dotenv(override=True, encoding="utf-8")

API_KEY = os.getenv("BINANCE_API_KEY")
API_SECRET = os.getenv("BINANCE_SECRET_KEY")
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

def get_balances() -> dict:
    """Lee los balances reales de USDT y BTC desde la cuenta de Binance."""
    try:
        account = _client().account()
        balances = {b['asset']: float(b['free']) + float(b['locked']) for b in account['balances']}
        return {
            'USDT': balances.get('USDT', 0.0),
            'BTC': balances.get('BTC', 0.0),
        }
    except Exception as e:
        return {'error': str(e), 'USDT': 0.0, 'BTC': 0.0}

