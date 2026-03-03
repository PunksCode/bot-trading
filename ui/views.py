from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Portfolio, PortfolioSnapshot
import json


@login_required
def dashboard(request):
    wallet = Portfolio.objects.first()
    
    # Si no hay wallet cargada, enviamos ceros para no romper la UI
    if not wallet:
        return render(request, "ui/dashboard.html", {"error": "Portafolio no inicializado."})

    snapshots = PortfolioSnapshot.objects.order_by('-timestamp')[:100]
    snapshots = list(reversed(snapshots))

    fechas = [s.timestamp.strftime("%H:%M") for s in snapshots]
    equity_data = [s.equity for s in snapshots]

    total_equity = wallet.usdt_balance + wallet.btc_balance
    pnl_usd = total_equity - wallet.initial_capital
    pnl_pct = (pnl_usd / wallet.initial_capital) * 100 if wallet.initial_capital > 0 else 0

    context = {
        "equity_total": round(total_equity, 2),
        "usdt_balance": round(wallet.usdt_balance, 2),
        "btc_balance": round(wallet.btc_balance, 4),
        "initial_capital": round(wallet.initial_capital, 2),
        "pnl_usd": round(pnl_usd, 2),
        "pnl_pct": round(pnl_pct, 2),
        "fechas_json": json.dumps(fechas),
        "equity_json": json.dumps(equity_data),
    }

    return render(request, "ui/dashboard.html", context)

