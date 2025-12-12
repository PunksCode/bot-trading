import pandas as pd
import os
import numpy as np
import yfinance as yf
import tensorflow as tf
from ta.momentum import RSIIndicator
from ta.volatility import BollingerBands
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint

# 1. GPU CHECK
print("\n" + "="*40)
print("🚀 INICIANDO ENTRENAMIENTO V2 (Librería TA)")
print("="*40)
gpus = tf.config.list_physical_devices('GPU')
if gpus:
    print(f"✅ GPU DETECTADA: {gpus[0].name}")
else:
    print("⚠️ ADVERTENCIA: Usando CPU")

# 2. DATOS
SYMBOL = 'BTC-USD'
print(f"\n📥 Descargando datos de {SYMBOL}...")
df = yf.download(SYMBOL, start='2020-01-01', interval='1d')

# Aplanar multi-índice si es necesario (yfinance a veces devuelve tablas complejas)
if isinstance(df.columns, pd.MultiIndex):
    df.columns = df.columns.get_level_values(0)

# 3. INDICADORES (Usando librería 'ta')
print("🧠 Calculando indicadores técnicos...")

# RSI (14 periodos)
rsi_indicator = RSIIndicator(close=df["Close"], window=14)
df["RSI"] = rsi_indicator.rsi()

# Bandas de Bollinger (20 periodos)
bb_indicator = BollingerBands(close=df["Close"], window=20, window_dev=2)
df["BB_High"] = bb_indicator.bollinger_hband()
df["BB_Low"] = bb_indicator.bollinger_lband()

# Limpiar nulos
df.dropna(inplace=True)

# Seleccionamos Features
feature_cols = ['Close', 'RSI', 'BB_High', 'BB_Low']
data = df[feature_cols].values
print(f"📊 Entrenando con: {feature_cols}")

# 4. PREPARACIÓN
scaler = MinMaxScaler(feature_range=(0, 1))
scaled_data = scaler.fit_transform(data)

PREDICTION_DAYS = 60
x_train, y_train = [], []

for x in range(PREDICTION_DAYS, len(scaled_data)):
    x_train.append(scaled_data[x-PREDICTION_DAYS:x])
    # Queremos predecir el Precio de Cierre (Columna 0)
    y_train.append(scaled_data[x, 0])

x_train, y_train = np.array(x_train), np.array(y_train)

# 5. MODELO
model = Sequential()
model.add(LSTM(units=50, return_sequences=True, input_shape=(x_train.shape[1], x_train.shape[2])))
model.add(Dropout(0.2))
model.add(LSTM(units=50, return_sequences=False))
model.add(Dropout(0.2))
model.add(Dense(units=1))

model.compile(optimizer='adam', loss='mean_squared_error')

# 6. ENTRENAMIENTO
print("\n🥊 COMIENZA EL ENTRENAMIENTO...")
if not os.path.exists('research'):
    os.makedirs('research')

callbacks = [
    EarlyStopping(monitor='loss', patience=5),
    ModelCheckpoint('research/modelo_btc_v2.h5', save_best_only=True, monitor='loss')
]

model.fit(x_train, y_train, epochs=50, batch_size=32, callbacks=callbacks)

print("\n" + "="*40)
print("✅ ¡LISTO! Modelo V2 guardado en: research/modelo_btc_v2.h5")
print("="*40)