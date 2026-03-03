from django.db import models

class Portfolio(models.Model):
    usdt_balance = models.FloatField(default=10000.0)
    btc_balance = models.FloatField(default=0.0)
    last_updated = models.DateTimeField(auto_now=True)
    
    # Métrica de salud
    initial_capital = models.FloatField(default=10000.0)

class SystemState(models.Model):
    """El Cerebro Central: Define el Régimen y la Estrategia Activa"""
    REGIME_CHOICES = [
        ('RANGING', 'Lateral (Rango)'),
        ('UNCERTAIN', 'Incierto (Volátil)'),
        ('TRENDING', 'Tendencia Fuerte (Peligro)'),
    ]
    STRATEGY_CHOICES = [
        ('GRID_V11', 'Grid Bot (Acumulación)'),
        ('SHANNON_V13', 'Shannon (Protección)'),
        ('IDLE', 'Modo Espera (Cash/Hold)'),
    ]
    
    current_regime = models.CharField(max_length=20, choices=REGIME_CHOICES, default='UNCERTAIN')
    active_strategy = models.CharField(max_length=20, choices=STRATEGY_CHOICES, default='IDLE')
    
    # Parámetros dinámicos calculados por el DecisionEngine
    volatility_score = models.FloatField(default=0.0) # ATR %
    trend_score = models.FloatField(default=0.0)      # ADX
    
    last_switch = models.DateTimeField(auto_now=True)

    # NUEVOS CAMPOS PARA PERSISTENCIA
    pending_regime = models.CharField(max_length=20, default='NONE')
    confirmation_count = models.IntegerField(default=0)
    
    # MÉTRICAS DE SALUD (Punto 3)
    peak_equity = models.FloatField(default=10000.0) # High Watermark
    max_drawdown = models.FloatField(default=0.0)    # Peor caída registrada

    # --- PARÁMETROS DE APRENDIZAJE (META-LEARNING) ---
    # Estos valores se actualizan con el optimizador
    param_adx_max = models.FloatField(default=25.0)    # Límite para activar Grid
    param_atr_mult = models.FloatField(default=4.0)    # Multiplicador del rango
    
    last_optimization = models.DateTimeField(null=True, blank=True) # Cuándo aprendimos

class ActiveOrder(models.Model):
    """Órdenes vivas (usadas por el Grid)"""
    SIDE_CHOICES = [('BUY', 'COMPRA'), ('SELL', 'VENTA')]
    price = models.FloatField()
    amount_usdt = models.FloatField()
    side = models.CharField(max_length=4, choices=SIDE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

class TradeHistory(models.Model):
    """Bitácora unificada"""
    strategy_used = models.CharField(max_length=20)
    action = models.CharField(max_length=50) # Ej: "Grid Arbitrage", "Shannon Rebalance"
    pnl_realized = models.FloatField(default=0.0)
    timestamp = models.DateTimeField(auto_now_add=True)
class PortfolioSnapshot(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    equity = models.FloatField()
    pnl_usd = models.FloatField()
    pnl_percent = models.FloatField()
    strategy_used = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.timestamp} - ${self.equity}"
