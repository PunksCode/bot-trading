import pandas_ta as ta

# Defaults si la DB no está disponible
DEFAULT_ADX_MAX = 25.0
DEFAULT_ATR_MULT = 4.0

class DecisionEngine:
    def __init__(self, df_context):
        # df_context debe traer velas de 4H para régimen macro
        self.df = df_context
        self.current = df_context.iloc[-1]

        # Leer parámetros APRENDIDOS del optimizer (DB)
        try:
            from .models import SystemState
            state = SystemState.objects.first()
            if state:
                self.adx_max = state.param_adx_max
                self.atr_mult = state.param_atr_mult
            else:
                self.adx_max = DEFAULT_ADX_MAX
                self.atr_mult = DEFAULT_ATR_MULT
        except Exception:
            self.adx_max = DEFAULT_ADX_MAX
            self.atr_mult = DEFAULT_ATR_MULT

    def detectar_regimen(self):
        """
        Salida: (regime_code, recommended_strategy, reason)
        Usa parámetros dinámicos del optimizer (param_adx_max, param_atr_mult)
        """
        # 1. CALCULO DE INDICADORES
        adx = self.df.ta.adx(length=14)['ADX_14'].iloc[-1]
        atr = self.df.ta.atr(length=14).iloc[-1]
        close = self.current['close']
        
        # Volatilidad Relativa (% del precio)
        atr_pct = (atr / close) * 100
        
        # Distancia a la EMA 200 (Tendencia Macro)
        ema_200 = self.df.ta.ema(length=200).iloc[-1]
        dist_ema = abs(close - ema_200) / close
        
        # 2. LÓGICA DE CLASIFICACIÓN (V2: parámetros del optimizer)
        
        # A. FILTRO DE SEGURIDAD (TENDENCIA FUERTE / CRASH)
        # Si el ADX es extremo (>40) o estamos lejísimos de la media (>15%)
        # El mercado está roto. NO OPERAR.
        if adx > 40 or dist_ema > 0.15:
            return "TRENDING", "IDLE", f"Mercado peligroso (ADX {round(adx,1)})"
            
        # B. DETECTOR DE RANGO (GRID) — usa adx_max del optimizer
        if adx < self.adx_max and 0.5 < atr_pct < 3.0:
            return "RANGING", "GRID_V11", f"Lateral (ADX {round(adx,1)} < {self.adx_max})"
            
        # C. ZONA DE INCERTIDUMBRE (SHANNON)
        return "UNCERTAIN", "SHANNON_V13", f"Incertidumbre (Volat {round(atr_pct,2)}%)"

    def get_grid_params(self):
        """Calcula parámetros dinámicos para el Grid — usa atr_mult del optimizer"""
        atr = self.df.ta.atr(length=14).iloc[-1]
        close = self.current['close']
        
        # El rango usa el multiplicador aprendido
        rango = atr * self.atr_mult
        return close - rango, close + rango  # Lower, Upper