import pandas_ta as ta

class DecisionEngine:
    def __init__(self, df_context):
        # df_context debe traer velas de 4H para régimen macro
        self.df = df_context
        self.current = df_context.iloc[-1]

    def detectar_regimen(self):
        """
        Salida: (regime_code, recommended_strategy, reason)
        """
        # LÓGICA DEMO / PLACEHOLDER
        # Esta versión es pública y simplificada.
        
        adx = self.df.ta.adx(length=14)['ADX_14'].iloc[-1]
        
        if adx > 25:
            return "TRENDING", "IDLE", "Tendencia detectada (Demo)"
            
        return "RANGING", "GRID_V11", "Rango detectado (Demo)"

    def get_grid_params(self):
        """Calcula parámetros dinámicos para el Grid si se activa"""
        # Parámetros genéricos para la versión pública
        close = self.current['close']
        return close * 0.95, close * 1.05 # +/- 5%
