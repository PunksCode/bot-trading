from django.db import models

class StrategyConfig(models.Model):
    name = models.CharField(max_length=50, default="sma_cross")
    param_fast = models.IntegerField(default=10)
    param_slow = models.IntegerField(default=20)
    is_enabled = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} ({'ON' if self.is_enabled else 'OFF'})"

class Trade(models.Model):
    side = models.CharField(max_length=4)  # BUY/SELL
    symbol = models.CharField(max_length=20)
    qty = models.FloatField()
    price = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    order_id = models.CharField(max_length=64, blank=True)
    status = models.CharField(max_length=20, default="NEW")
    error = models.TextField(blank=True)

    def __str__(self):
        return f"{self.side} {self.symbol} @ {self.price}"
