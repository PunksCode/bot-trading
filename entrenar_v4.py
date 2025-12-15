import ccxt
import pandas as pd
import numpy as np
import os
import time
from datetime import datetime, timedelta

# Indicadores
from ta.momentum import RSIIndicator
from ta.volatility import BollingerBands
from ta.volume import OnBalanceVolumeIndicator # <--- NUEVO INVITADO

from sklearn.preprocessing import MinMaxScaler
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint

# ==========================================
# CONFIGURACIÓN V4 (VOLUMEN)
# ==========================================
SYMBOL = 'BTC/USDT'
TIMEFRAME = '15m'
DAYS_TO_DOWNLOAD = 90
PREDICTION_STEPS = 96
EPOCHS = 50

print("="*50)
print(f"🚀 INICIANDO ENTRENAMIENTO V4 (VOLUMEN + OBV)")
print("="*50)

# 1. DOWNLOADER (Igual que antes)
def fetch_binance_history(symbol, timeframe, days):
    exchange = ccxt.binance({'enableRateLimit': True})
    start_date = datetime.now() - timedelta(days=days)
    since = int(start_date.timestamp() * 1000)
    all_candles = []
    print(f"📥 Descargando datos...")
    
    while True:
        try:
            candles = exchange.fetch_ohlcv(symbol, timeframe, since=since, limit=1000)
            if not candles: break
            all_candles += candles
            last_time = candles[-1][0]
            since = last_time + 1
            print(f"   ... {len(all_candles)} velas")
            if last_time >= int(time.time() * 1000): break
            time.sleep(0.1)
        except Exception as e:
            print(f"❌ Error: {e}")
            break
            
    df = pd.DataFrame(all_candles, columns=['timestamp', 'Open', 'High', 'Low', 'Close', 'Volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df.set_index('timestamp', inplace=True)
    return df

df = fetch_binance_history(SYMBOL, TIMEFRAME, DAYS_TO_DOWNLOAD)

# ==========================================
# 2. FEATURE ENGINEERING (NUEVO: VOLUMEN)
# ==========================================
print("\n🧠 Calculando Indicadores (RSI, Bandas, OBV)...")

# A. Indicadores de Precio
rsi_indicator = RSIIndicator(close=df["Close"], window=14)
df["RSI"] = rsi_indicator.rsi()

bb_indicator = BollingerBands(close=df["Close"], window=20, window_dev=2)
df["BB_High"] = bb_indicator.bollinger_hband()
df["BB_Low"] = bb_indicator.bollinger_lband()

# B. Indicadores de Volumen (¡LA CLAVE!)
obv_indicator = OnBalanceVolumeIndicator(close=df["Close"], volume=df["Volume"])
df["OBV"] = obv_indicator.on_balance_volume()

# Limpieza
df.dropna(inplace=True)

# Seleccionamos 6 variables ahora
feature_cols = ['Close', 'RSI', 'BB_High', 'BB_Low', 'Volume', 'OBV']
data = df[feature_cols].values
print(f"📊 Features: {feature_cols}")

# ==========================================
# 3. ESCALADO INTELIGENTE
# ==========================================
# Usamos un Scaler para todo, pero es importante notar que el Volumen
# tiene escalas muy diferentes al precio. MinMax lo maneja bien.
scaler = MinMaxScaler(feature_range=(0, 1))
scaled_data = scaler.fit_transform(data)

# Preparamos X (Inputs) e Y (Target = Solo Precio de Cierre)
x_train, y_train = [], []

for x in range(PREDICTION_STEPS, len(scaled_data)):
    x_train.append(scaled_data[x-PREDICTION_STEPS:x])
    y_train.append(scaled_data[x, 0]) # Target es la columna 0 (Close)

x_train, y_train = np.array(x_train), np.array(y_train)

# ==========================================
# 4. MODELO LSTM V4
# ==========================================
model = Sequential()
# Input shape ahora recibe 6 features automáticamente
model.add(LSTM(units=64, return_sequences=True, input_shape=(x_train.shape[1], x_train.shape[2])))
model.add(Dropout(0.2))
model.add(LSTM(units=64, return_sequences=False))
model.add(Dropout(0.2))
model.add(Dense(units=1))

model.compile(optimizer='adam', loss='mean_squared_error')

if not os.path.exists('research'):
    os.makedirs('research')

callbacks = [
    EarlyStopping(monitor='loss', patience=6),
    ModelCheckpoint('research/modelo_btc_v4_vol.h5', save_best_only=True, monitor='loss')
]

print("\n🥊 ENTRENANDO MODELO V4 (CON VOLUMEN)...")
model.fit(x_train, y_train, epochs=EPOCHS, batch_size=32, callbacks=callbacks)

print("\n✅ MODELO V4 GUARDADO: research/modelo_btc_v4_vol.h5")