from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import os

from core.scheduler import start, stop, sched
from core.exchange import get_price, ping
from core.executor import execute_signal
from .models import StrategyConfig, Trade
from django.core.cache import cache
from core.exchange import get_price

SYMBOL = os.getenv("SYMBOL", "SOLUSDT")
TRADE_QTY = float(os.getenv("TRADE_QTY", "0.1"))

@login_required
def dashboard(request):
    cfg = StrategyConfig.objects.first() or StrategyConfig.objects.create(is_enabled=False)
    price = None
    ok = False
    try:
        ok = ping()
        price = get_price(SYMBOL) if ok else None
    except Exception as e:
        price = None
    ctx = {
        "cfg": cfg, "trades": Trade.objects.order_by("-created_at")[:30],
        "running": getattr(sched, "running", False),
        "connected": ok, "symbol": SYMBOL, "price": price, "qty": TRADE_QTY
    }
    return render(request, "dashboard.html", ctx)

@login_required
def toggle_bot(request):
    cfg = StrategyConfig.objects.first() or StrategyConfig.objects.create()
    cfg.is_enabled = not cfg.is_enabled
    cfg.save()
    if cfg.is_enabled: start()
    else: stop()
    return redirect("dashboard")

@login_required
def buy(request):
    res = execute_signal(SYMBOL, "BUY", TRADE_QTY)
    Trade.objects.create(
        side="BUY", symbol=SYMBOL, qty=TRADE_QTY,
        price=res.get("price") or 0.0,
        order_id=str(res.get("order_id") or ""),
        status=res.get("status"), error=str(res.get("error") or "")
    )
    return redirect("dashboard")

@login_required
def sell(request):
    res = execute_signal(SYMBOL, "SELL", TRADE_QTY)
    Trade.objects.create(
        side="SELL", symbol=SYMBOL, qty=TRADE_QTY,
        price=res.get("price") or 0.0,
        order_id=str(res.get("order_id") or ""),
        status=res.get("status"), error=str(res.get("error") or "")
    )
    return redirect("dashboard")

@login_required
def price_json(request):
    # tratá de usar el último precio del WS; si no hay, caé a REST
    price = cache.get("last_price")
    if price is None:
        try:
            price = get_price(SYMBOL)
            cache.set("last_price", price, timeout=15)
        except Exception as e:
            return JsonResponse({"ok": False, "error": str(e)}, status=500)
    return JsonResponse({"ok": True, "symbol": SYMBOL, "price": float(price)})

