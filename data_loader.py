import ccxt
import pandas as pd
import time
from datetime import datetime

print("🚀 INICIANDO CONEXIÓN CON BINANCE (Vía CCXT)...")

# 1. Configurar el Exchange (Binance)
# No necesitamos claves API todavía para bajar precios públicos
exchange = ccxt.binance({
    'enableRateLimit': True, # Importante para que Binance no nos bloquee por pedir muy rápido
})

def obtener_datos(symbol, timeframe, limit=1000):
    """
    Baja las últimas 'limit' velas.
    Binance suele dar máximo 1000 velas por llamada.
    """
    print(f"📥 Descargando {symbol} en {timeframe}...")
    
    try:
        # fetch_ohlcv baja: Open, High, Low, Close, Volume
        bars = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
        
        # Convertimos a Tabla de Pandas
        df = pd.DataFrame(bars, columns=['timestamp', 'Open', 'High', 'Low', 'Close', 'Volume'])
        
        # Arreglamos la fecha (Binance manda milisegundos)
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('timestamp', inplace=True)
        
        return df

    except Exception as e:
        print(f"❌ Error descargando datos: {e}")
        return None

# --- PRUEBA DEL SCRIPT ---
if __name__ == "__main__":
    # Probamos bajar BTC/USDT en velas de 15 minutos
    # Nota: En ccxt los símbolos son 'BTC/USDT', no 'BTC-USD'
    df = obtener_datos('BTC/USDT', '15m', limit=100) 
    
    if df is not None:
        print("\n✅ ¡DATOS RECIBIDOS CORRECTAMENTE!")
        print(df.tail()) # Muestra las últimas 5 filas
        print(f"\nTotal de velas: {len(df)}")
        
        # Guardar en CSV para inspeccionar
        df.to_csv("datos_binance_15m.csv")
        print("💾 Guardado en 'datos_binance_15m.csv'")
    else:
        print("Algo falló.")
