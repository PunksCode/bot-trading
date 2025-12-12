import os
import ccxt
import numpy as np
import pandas as pd
from django.conf import settings
from tensorflow.keras.models import load_model
from sklearn.preprocessing import MinMaxScaler
from ta.momentum import RSIIndicator
from ta.volatility import BollingerBands

# ==========================================
# CONFIGURACIÓN V3 (INTRADÍA)
# ==========================================
SYMBOL_BINANCE = 'BTC/USDT'  # Formato para CCXT
TIMEFRAME = '15m'            # Velas de 15 minutos
PREDICTION_STEPS = 96        # El modelo espera ver las últimas 24h (96 velas)
MODEL_NAME = 'modelo_btc_v3_15m.h5'

# Ruta al modelo
MODEL_PATH = os.path.join(settings.BASE_DIR, 'research', MODEL_NAME)

def obtener_datos_binance(limit=200):
    """Baja las últimas velas directamente de Binance"""
    exchange = ccxt.binance({'enableRateLimit': True})
    try:
        # Bajamos OHLCV
        bars = exchange.fetch_ohlcv(SYMBOL_BINANCE, timeframe=TIMEFRAME, limit=limit)
        df = pd.DataFrame(bars, columns=['timestamp', 'Open', 'High', 'Low', 'Close', 'Volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('timestamp', inplace=True)
        return df
    except Exception as e:
        print(f"Error conectando con Binance: {e}")
        return None

def predecir_precio_futuro():
    try:
        if not os.path.exists(MODEL_PATH):
            return {"error": f"Modelo no encontrado: {MODEL_NAME}. ¿Ejecutaste entrenar_v3.py?"}

        # 1. OBTENER DATOS REALES (Binance)
        # Necesitamos suficiente historia para:
        # a) Calcular RSI/Bandas (requiere ~20 velas previas)
        # b) Llenar la ventana de predicción (96 velas)
        df = obtener_datos_binance(limit=200)

        if df is None or len(df) < (PREDICTION_STEPS + 20):
            return {"error": "Binance no devolvió suficientes datos."}

        # 2. CALCULAR INDICADORES (Igual que en el entrenamiento)
        rsi = RSIIndicator(close=df["Close"], window=14)
        df["RSI"] = rsi.rsi()

        bb = BollingerBands(close=df["Close"], window=20, window_dev=2)
        df["BB_High"] = bb.bollinger_hband()
        df["BB_Low"] = bb.bollinger_lband()

        df.dropna(inplace=True)

        # 3. PREPARAR ESCALADO
        feature_cols = ['Close', 'RSI', 'BB_High', 'BB_Low']
        data = df[feature_cols].values

        # Tomamos exactamente los últimos 96 pasos (Ventana de 24h)
        last_window = data[-PREDICTION_STEPS:] 
        
        # Escalamos (0 a 1)
        scaler = MinMaxScaler(feature_range=(0, 1))
        scaler.fit(data) # Ajustamos con los datos recientes para tener la escala correcta
        
        last_window_scaled = scaler.transform(last_window)

        # Formato para TensorFlow: (1 muestra, 96 pasos, 4 features)
        X_test = np.array([last_window_scaled])
        
        # 4. PREDICCIÓN
        model = load_model(MODEL_PATH)
        pred_scaled = model.predict(X_test)

        # 5. DES-ESCALAR
        # Truco: Creamos una fila "dummy" con la predicción en la pos 0
        dummy_row = np.zeros((1, len(feature_cols)))
        dummy_row[0, 0] = pred_scaled[0][0]
        
        pred_price = scaler.inverse_transform(dummy_row)[0, 0]
        
        # Datos actuales
        current_price = float(df['Close'].iloc[-1])
        
        # Lógica de Tendencia (Más sensible para Intradía)
        diff = pred_price - current_price
        pct_change = (diff / current_price) * 100
        
        tendencia = "NEUTRAL 😐"
        if pct_change > 0.1: tendencia = "ALCISTA 🚀"
        elif pct_change < -0.1: tendencia = "BAJISTA 🔻"

        return {
            "moneda": "BTC/USDT (Binance 15m)",
            "precio_actual": round(current_price, 2),
            "prediccion_mañana": round(pred_price, 2), # En realidad es "próxima vela/periodo"
            "tendencia": tendencia,
            "porcentaje": round(pct_change, 2),
            "indicadores": {
                "rsi": round(df['RSI'].iloc[-1], 2),
                "volatilidad": "Alta" if (df['BB_High'].iloc[-1] - df['BB_Low'].iloc[-1]) > (current_price * 0.02) else "Normal"
            }
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"error": str(e)}