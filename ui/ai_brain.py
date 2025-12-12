import os
import numpy as np
import pandas as pd
import yfinance as yf
from django.conf import settings
from tensorflow.keras.models import load_model
from sklearn.preprocessing import MinMaxScaler
from ta.momentum import RSIIndicator
from ta.volatility import BollingerBands

# CONFIGURACIÓN
SYMBOL = 'BTC-USD'
# IMPORTANTE: Apuntamos al nuevo modelo V2
MODEL_PATH = os.path.join(settings.BASE_DIR, 'research', 'modelo_btc_v2.h5')

def predecir_precio_futuro():
    """
    1. Descarga datos.
    2. Calcula indicadores (RSI, BB).
    3. Prepara los datos para el modelo V2.
    4. Predice.
    """
    try:
        if not os.path.exists(MODEL_PATH):
            return {"error": f"No encuentro el modelo en: {MODEL_PATH}"}

        # 1. OBTENER DATOS (Bajamos 6 meses para tener espacio para calcular indicadores)
        # Necesitamos historial suficiente para que el RSI sea preciso
        df = yf.download(SYMBOL, period='6mo', interval='1d')
        
        # Corrección para yfinance nuevo (aplanar índices si vienen complejos)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        if len(df) < 80:
            return {"error": "No hay suficientes datos de mercado."}

        # 2. CALCULAR INDICADORES (Igual que en el entrenamiento)
        # RSI
        rsi = RSIIndicator(close=df["Close"], window=14)
        df["RSI"] = rsi.rsi()

        # Bandas Bollinger
        bb = BollingerBands(close=df["Close"], window=20, window_dev=2)
        df["BB_High"] = bb.bollinger_hband()
        df["BB_Low"] = bb.bollinger_lband()

        # Limpiamos nulos (los primeros días no tienen cálculo)
        df.dropna(inplace=True)

        # Seleccionamos las mismas columnas que usamos al entrenar
        feature_cols = ['Close', 'RSI', 'BB_High', 'BB_Low']
        data = df[feature_cols].values

        # 3. PREPARAR ESCALADO
        # Tomamos los últimos 60 días
        last_60_days = data[-60:]
        
        # Escalamos (El modelo necesita ver todo entre 0 y 1)
        scaler = MinMaxScaler(feature_range=(0, 1))
        # Ajustamos el scaler con todos los datos recientes para tener referencia
        scaler.fit(data) 
        
        last_60_days_scaled = scaler.transform(last_60_days)

        # Formato para TensorFlow: (1 muestra, 60 pasos, 4 features)
        X_test = np.array([last_60_days_scaled])
        
        # 4. PREDICCIÓN
        model = load_model(MODEL_PATH)
        pred_scaled = model.predict(X_test)

        # 5. INVERTIR ESCALA
        # El modelo devuelve 1 solo valor (el precio escalado).
        # Pero el scaler espera 4 columnas. Hacemos un truco para des-escalar:
        # Creamos una fila falsa con la predicción en la columna 0 y ceros en el resto
        dummy_row = np.zeros((1, len(feature_cols)))
        dummy_row[0, 0] = pred_scaled[0][0]
        
        pred_price = scaler.inverse_transform(dummy_row)[0, 0]
        
        # Datos actuales para comparar
        current_price = float(df['Close'].iloc[-1])
        
        # Tendencia
        tendencia = "ALCISTA 🚀" if pred_price > current_price else "BAJISTA 🔻"
        cambio_pct = ((pred_price - current_price) / current_price) * 100

        return {
            "moneda": SYMBOL,
            "precio_actual": round(current_price, 2),
            "prediccion_mañana": round(pred_price, 2),
            "tendencia": tendencia,
            "porcentaje": round(cambio_pct, 2),
            "indicadores": {
                "rsi": round(df['RSI'].iloc[-1], 2),
                "volatilidad": "Alta" if (df['BB_High'].iloc[-1] - df['BB_Low'].iloc[-1]) > 2000 else "Normal"
            }
        }

    except Exception as e:
        import traceback
        traceback.print_exc() # Esto imprimirá el error real en la terminal negra
        return {"error": str(e)}