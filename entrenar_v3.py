import ccxt
import pandas as pd
import numpy as np
import os
import time
from datetime import datetime, timedelta

# Indicadores e IA
from ta.momentum import RSIIndicator
from ta.volatility import BollingerBands
from sklearn.preprocessing import MinMaxScaler
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint

# ==========================================
# CONFIGURACIÓN
# ==========================================
SYMBOL = 'BTC/USDT'     # Formato Binance
TIMEFRAME = '15m'       # Velas de 15 minutos
DAYS_TO_DOWNLOAD = 90   # Bajamos los últimos 3 meses (aprox 8.600 velas)
PREDICTION_STEPS = 96   # La IA mirará las últimas 24h (96 velas de 15m) para decidir
EPOCHS = 50

print("="*50)
print(f"🚀 INICIANDO ENTRENAMIENTO V3 ({TIMEFRAME}) VÍA BINANCE")
print("="*50)

# 1. FUNCIÓN PARA BAJAR HISTORIA LARGA
def fetch_binance_history(symbol, timeframe, days):
    exchange = ccxt.binance({'enableRateLimit': True})
    
    # Calcular fecha de inicio en milisegundos
    start_date = datetime.now() - timedelta(days=days)
    since = int(start_date.timestamp() * 1000)
    
    all_candles = []
    print(f"📥 Descargando {days} días de datos de {symbol}...")
    
    while True:
        try:
            # Bajar lote de 1000 velas
            candles = exchange.fetch_ohlcv(symbol, timeframe, since=since, limit=1000)
            
            if not candles:
                break
                
            all_candles += candles
            
            # Actualizar el tiempo para el siguiente lote (último tiempo + 1ms)
            last_time = candles[-1][0]
            since = last_time + 1
            
            # Barra de progreso simple
            print(f"   ... Descargadas {len(all_candles)} velas hasta ahora")
            
            # Si llegamos al presente, paramos
            if last_time >= int(time.time() * 1000):
                break
                
            # Pequeña pausa para no molestar a Binance
            time.sleep(0.1)
            
        except Exception as e:
            print(f"❌ Error en descarga: {e}")
            break
            
    # Crear DataFrame
    df = pd.DataFrame(all_candles, columns=['timestamp', 'Open', 'High', 'Low', 'Close', 'Volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df.set_index('timestamp', inplace=True)
    
    print(f"✅ Descarga completa: {len(df)} velas totales.")
    return df

# ==========================================
# 2. EJECUCIÓN
# ==========================================

# A. Bajar Datos
df = fetch_binance_history(SYMBOL, TIMEFRAME, DAYS_TO_DOWNLOAD)

# B. Calcular Indicadores (Feature Engineering)
print("\n🧠 Calculando RSI y Bandas de Bollinger...")
rsi_indicator = RSIIndicator(close=df["Close"], window=14)
df["RSI"] = rsi_indicator.rsi()

bb_indicator = BollingerBands(close=df["Close"], window=20, window_dev=2)
df["BB_High"] = bb_indicator.bollinger_hband()
df["BB_Low"] = bb_indicator.bollinger_lband()

df.dropna(inplace=True)

# C. Preparar Datos para IA
feature_cols = ['Close', 'RSI', 'BB_High', 'BB_Low']
data = df[feature_cols].values
print(f"📊 Features seleccionadas: {feature_cols}")

scaler = MinMaxScaler(feature_range=(0, 1))
scaled_data = scaler.fit_transform(data)

x_train, y_train = [], []

for x in range(PREDICTION_STEPS, len(scaled_data)):
    # Input: Ventana de tiempo anterior (96 velas = 24h)
    x_train.append(scaled_data[x-PREDICTION_STEPS:x])
    # Target: Precio de Cierre actual
    y_train.append(scaled_data[x, 0])

x_train, y_train = np.array(x_train), np.array(y_train)

# D. Construir Modelo
print(f"\n🏗️ Construyendo LSTM (Input shape: {x_train.shape[1]} pasos, {x_train.shape[2]} features)...")
model = Sequential()
model.add(LSTM(units=64, return_sequences=True, input_shape=(x_train.shape[1], x_train.shape[2])))
model.add(Dropout(0.2))
model.add(LSTM(units=64, return_sequences=False))
model.add(Dropout(0.2))
model.add(Dense(units=1))

model.compile(optimizer='adam', loss='mean_squared_error')

# E. Entrenar
if not os.path.exists('research'):
    os.makedirs('research')

callbacks = [
    EarlyStopping(monitor='loss', patience=5),
    ModelCheckpoint('research/modelo_btc_v3_15m.h5', save_best_only=True, monitor='loss')
]

print("\n🥊 INICIANDO ENTRENAMIENTO (Esto puede tardar un poco más)...")
model.fit(x_train, y_train, epochs=EPOCHS, batch_size=32, callbacks=callbacks)

print("\n" + "="*50)
print("✅ MODELO V3 (BINANCE 15m) GUARDADO EN: research/modelo_btc_v3_15m.h5")
print("="*50)
