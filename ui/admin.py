from django.contrib import admin
from .models import StrategyConfig, Trade

@admin.register(StrategyConfig)
class StrategyConfigAdmin(admin.ModelAdmin):
    list_display = ("name", "param_fast", "param_slow", "is_enabled")
    list_editable = ("param_fast", "param_slow", "is_enabled")

@admin.register(Trade)
class TradeAdmin(admin.ModelAdmin):
    list_display = ("created_at", "side", "symbol", "price", "qty", "status")
    list_filter = ("side", "status", "symbol")
    search_fields = ("order_id",)


