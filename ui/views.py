from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .trader import ejecutar_sistema
import ccxt
import pandas as pd

def get_market_data():
    """Descarga las últimas 200 velas de 4H para el análisis de régimen"""
    exchange = ccxt.binance()
    try:
        # Descargamos 4H para el Decision Engine (Macro)
        ohlcv = exchange.fetch_ohlcv('BTC/USDT', '4h', limit=200)
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        return df
    except Exception as e:
        print(f"Error Binance: {e}")
        return pd.DataFrame()

@login_required
def dashboard(request):
    # 1. Obtener Datos Reales
    df = get_market_data()
    
    context = {}
    
    if not df.empty:
        precio_actual = df.iloc[-1]['close']
        
        # 2. Ejecutar el Sistema Híbrido
        # (Esto analiza el régimen, gestiona el grid/shannon y retorna el estado)
        resultado = ejecutar_sistema(df, precio_actual)
        
        context = {
            'precio': precio_actual,
            'regime': resultado['regime'],      # Ej: 'RANGING'
            'strategy': resultado['strategy'],  # Ej: 'GRID_V11'
            'message': resultado['message'],    # Logs del bot
            'equity': resultado['equity'],
            'usdt': resultado['usdt'],
            'btc': resultado['btc'],
            'dd': resultado.get('dd', 0.0),
            'max_dd': resultado.get('max_dd', 0.0),
        }
    else:
        context = {'message': 'Error de conexión con Binance API'}

    return render(request, 'ui/dashboard.html', context)