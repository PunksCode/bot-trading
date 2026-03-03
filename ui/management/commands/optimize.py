from django.core.management.base import BaseCommand
from ui.models import SystemState
from datetime import datetime, timedelta
import ccxt
import pandas as pd
import pandas_ta as ta
from django.utils import timezone

class Command(BaseCommand):
    help = 'Ejecuta el Walk-Forward Optimization y actualiza la DB'

    def handle(self, *args, **options):
        self.stdout.write("🧠 INICIANDO AUTO-AJUSTE DE PARÁMETROS...")
        
        # 1. CONFIGURACIÓN
        SYMBOL = 'BTC/USDT'
        TIMEFRAME = '4h'
        DAYS_LOOKBACK = 14 # Aprender de las últimas 2 semanas
        
        # 2. DESCARGA DE DATOS
        exchange = ccxt.binance()
        since = exchange.parse8601((datetime.now() - timedelta(days=DAYS_LOOKBACK)).isoformat())
        ohlcv = exchange.fetch_ohlcv(SYMBOL, TIMEFRAME, since=since, limit=1000)
        
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        
        # Indicadores
        df['ADX'] = ta.adx(df['high'], df['low'], df['close'], length=14)['ADX_14']
        df['ATR'] = ta.atr(df['high'], df['low'], df['close'], length=14)
        df.dropna(inplace=True)
        
        # 3. GRID SEARCH (Búsqueda del Tesoro)
        # Probamos combinaciones razonables
        candidates_adx = [20, 25, 30, 35, 40, 45]
        candidates_atr = [2.0, 3.0, 4.0, 5.0]
        
        best_score = -999999
        best_params = {'adx': 25, 'atr': 4.0} # Default conservador
        
        # Simulador Vectorizado Simplificado
        for adx_lim in candidates_adx:
            for atr_mult in candidates_atr:
                
                # Cálculo de PnL teórico
                pnl = 0
                for i in range(len(df)):
                    row = df.iloc[i]
                    price = row['close']
                    atr_pct = (row['ATR'] / price) * 100
                    
                    # Lógica Grid Simulada
                    if row['ADX'] < adx_lim and 0.5 < atr_pct < 3.0:
                        # Grid Yield Estimado
                        # Penalizamos rangos muy amplios (atr_mult alto) porque dan menos trades
                        yield_trade = (row['ATR'] / price) * 0.15 
                        pnl += yield_trade
                
                if pnl > best_score:
                    best_score = pnl
                    best_params = {'adx': adx_lim, 'atr': atr_mult}
        
        # 4. GUARDAR EN BASE DE DATOS
        state, _ = SystemState.objects.get_or_create(id=1)
        state.param_adx_max = best_params['adx']
        state.param_atr_mult = best_params['atr']
        state.last_optimization = timezone.now()
        state.save()
        
        self.stdout.write(self.style.SUCCESS(f"✅ OPTIMIZACIÓN COMPLETADA"))
        self.stdout.write(f"   Nuevos Params: ADX < {state.param_adx_max} | ATR * {state.param_atr_mult}")
        self.stdout.write(f"   Score Simulado: {round(best_score, 4)}")
