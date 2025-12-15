from django.contrib import admin
from .models import Portfolio, SystemState, ActiveOrder, TradeHistory

@admin.register(Portfolio)
class PortfolioAdmin(admin.ModelAdmin):
    list_display = ('usdt_balance', 'btc_balance', 'initial_capital', 'last_updated')

@admin.register(SystemState)
class SystemStateAdmin(admin.ModelAdmin):
    # Este es el panel de control del Cerebro
    list_display = ('current_regime', 'active_strategy', 'volatility_score', 'last_switch')

@admin.register(ActiveOrder)
class ActiveOrderAdmin(admin.ModelAdmin):
    # Órdenes vivas del Grid
    list_display = ('side', 'price', 'amount_usdt', 'created_at')

@admin.register(TradeHistory)
class TradeHistoryAdmin(admin.ModelAdmin):
    # La bitácora unificada
    list_display = ('timestamp', 'strategy_used', 'action', 'pnl_realized')
    list_filter = ('strategy_used', 'action')
    ordering = ('-timestamp',)