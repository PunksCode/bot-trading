import os
import ccxt
import numpy as np
import pandas as pd
from datetime import timedelta
from django.conf import settings
from tensorflow.keras.models import load_model
from sklearn.preprocessing import MinMaxScaler
# Importamos OBV también aquí
from ta.momentum import RSIIndicator
from ta.volatility import BollingerBands
from ta.volume import OnBalanceVolumeIndicator
from ta.trend import ADXIndicator
from ta.volatility import AverageTrueRange
from ui.bot_runtime import BOT_STATE
from django.utils import timezone

# CONFIGURACIÓN V4
SYMBOL_BINANCE = 'BTC/USDT'
TIMEFRAME = '15m'
PREDICTION_STEPS = 96
MODEL_NAME = 'modelo_btc_v4_vol.h5' # <--- OJO: Nombre nuevo

MODEL_PATH = os.path.join(settings.BASE_DIR, 'research', MODEL_NAME)

def obtener_datos_binance(limit=300): # Pedimos más datos para asegurar el cálculo de OBV
    exchange = ccxt.binance({'enableRateLimit': True})
    try:
        bars = exchange.fetch_ohlcv(SYMBOL_BINANCE, timeframe=TIMEFRAME, limit=limit)
        df = pd.DataFrame(bars, columns=['timestamp', 'Open', 'High', 'Low', 'Close', 'Volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('timestamp', inplace=True)
        return df
    except Exception as e:
        print(f"Error Binance: {e}")
        return None

def predecir_precio_futuro():
    try:
        if not os.path.exists(MODEL_PATH):
            return {"error": f"Falta el modelo V4: {MODEL_NAME}"}

        df = obtener_datos_binance(limit=300)
        if df is None or len(df) < 150:
            return {"error": "Datos insuficientes"}

        # --- CALCULAMOS LOS MISMOS INDICADORES QUE EN V4 ---
        rsi = RSIIndicator(close=df["Close"], window=14)
        df["RSI"] = rsi.rsi()

        bb = BollingerBands(close=df["Close"], window=20, window_dev=2)
        df["BB_High"] = bb.bollinger_hband()
        df["BB_Low"] = bb.bollinger_lband()

        # NUEVO: OBV
        obv = OnBalanceVolumeIndicator(close=df["Close"], volume=df["Volume"])
        df["OBV"] = obv.on_balance_volume()

        # NUEVO: ADX (Fuerza de Tendencia)
        adx_ind = ADXIndicator(high=df['High'], low=df['Low'], close=df['Close'], window=14)
        df['ADX'] = adx_ind.adx()

        # NUEVO: ATR (Volatilidad Real)
        atr_ind = AverageTrueRange(high=df['High'], low=df['Low'], close=df['Close'], window=14)
        df['ATR'] = atr_ind.average_true_range()

        df.dropna(inplace=True)

        # Seleccionamos las 6 columnas
        feature_cols = ['Close', 'RSI', 'BB_High', 'BB_Low', 'Volume', 'OBV']
        data = df[feature_cols].values

        last_window = data[-PREDICTION_STEPS:] 
        
        scaler = MinMaxScaler(feature_range=(0, 1))
        scaler.fit(data) 
        
        last_window_scaled = scaler.transform(last_window)
        X_test = np.array([last_window_scaled])
        
        # PREDICCIÓN
        model = load_model(MODEL_PATH)
        pred_scaled = model.predict(X_test)

        # DES-ESCALAR
        dummy_row = np.zeros((1, len(feature_cols)))
        dummy_row[0, 0] = pred_scaled[0][0]
        pred_price = scaler.inverse_transform(dummy_row)[0, 0]
        
        current_price = float(df['Close'].iloc[-1])
        
        diff = pred_price - current_price
        pct_change = (diff / current_price) * 100
        
        tendencia = "NEUTRAL 😐"
        if pct_change > 0.15: tendencia = "ALCISTA 🚀" # Hacemos un poco más exigente el umbral
        elif pct_change < -0.15: tendencia = "BAJISTA 🔻"

        # 1. CÁLCULO DE TIEMPO EXACTO
        # La última vela tiene una fecha. La predicción es para la SIGUIENTE vela (+15 min)
        last_candle_time = df.index[-1]
        target_time = last_candle_time + timedelta(minutes=15)
        # Ajustamos a hora local (esto depende de tu server, asumimos UTC o ajustamos)
        target_time_str = target_time.strftime('%H:%M') 

        # 2. ANÁLISIS DE VOLUMEN
        current_vol = df['Volume'].iloc[-1]
        avg_vol = df['Volume'].tail(20).mean() # Promedio de últimas 20 velas
        
        vol_state = "Normal"
        if current_vol > (avg_vol * 1.5):
            vol_state = "ALTO 🔥" # Mucha actividad
        elif current_vol < (avg_vol * 0.5):
            vol_state = "BAJO 💤" # Poco interés
        BOT_STATE.update({
            "last_update": timezone.now().strftime("%H:%M:%S"),
            "tendencia": tendencia,
            "precio_actual": round(current_price, 2),
            "prediccion": round(pred_price, 2),
            "mensaje": f"{tendencia} | Δ {round(pct_change,2)}%",
        })
        return {
            "moneda": "BTC/USDT (Binance 15m)",
            "precio_actual": round(current_price, 2),
            "prediccion_mañana": round(pred_price, 2),
            "tendencia": tendencia,
            "porcentaje": round(pct_change, 2),
            "meta_temporal": f"Cierre de vela: {target_time_str}",
            "indicadores": {
                "rsi": round(df['RSI'].iloc[-1], 2),
                "volatilidad": "Alta" if (df['BB_High'].iloc[-1] - df['BB_Low'].iloc[-1]) > (current_price * 0.02) else "Normal",
                "volumen": vol_state,
                "obv": round(df['OBV'].iloc[-1], 2),
                # AGREGAMOS ESTOS DOS:
                "adx": round(df['ADX'].iloc[-1], 2),
                "atr": round(df['ATR'].iloc[-1], 2)
            },
            "wallet": {"profit": 0, "usdt": 0, "btc": 0} 
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"error": str(e)}