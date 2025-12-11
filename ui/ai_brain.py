import os
import numpy as np
import pandas as pd
import yfinance as yf
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import load_model
from django.conf import settings

# Configuración
SYMBOL = 'BTC-USD'
MODEL_PATH = os.path.join(settings.BASE_DIR, 'research', 'modelo_btc_v1.h5')

def predecir_precio_futuro():
    """
    1. Descarga datos recientes.
    2. Carga el modelo entrenado.
    3. Devuelve la predicción y el precio actual.
    """
    try:
        # 1. Verificar si existe el modelo
        if not os.path.exists(MODEL_PATH):
            return {"error": "El cerebro (.h5) no se encuentra en la carpeta research."}

        # 2. Obtener datos en vivo (Necesitamos 60 días + un margen de seguridad)
        # Bajamos 90 días para asegurar que tengamos 60 velas válidas
        df = yf.download(SYMBOL, period='3mo', interval='1d')
        
        if len(df) < 60:
            return {"error": "No hay suficientes datos de mercado para predecir."}

        # Tomamos solo el precio de cierre
        data = df['Close'].values
        
        # 3. Preprocesamiento (Igual que en el entrenamiento)
        # Usamos los ultimos 60 días exactos
        last_60_days = data[-60:].reshape(-1, 1)
        
        # Escalamos entre 0 y 1
        scaler = MinMaxScaler(feature_range=(0, 1))
        scaler.fit(data.reshape(-1, 1)) # Ajustamos el scaler con todos los datos recientes
        
        last_60_days_scaled = scaler.transform(last_60_days)

        # Formato para TensorFlow: (1 muestra, 60 pasos, 1 feature)
        X_test = []
        X_test.append(last_60_days_scaled)
        X_test = np.array(X_test)
        X_test = np.reshape(X_test, (X_test.shape[0], X_test.shape[1], 1))

        # 4. Cargar el Cerebro y Predecir
        model = load_model(MODEL_PATH)
        pred_scaled = model.predict(X_test)

        # 5. Invertir la escala (De 0.5 a $45,000)
        pred_price = scaler.inverse_transform(pred_scaled)
        pred_price_final = float(pred_price[0][0])
        current_price = float(data[-1])

        # Calcular tendencia
        tendencia = "ALCISTA 🚀" if pred_price_final > current_price else "BAJISTA 🔻"
        cambio_pct = ((pred_price_final - current_price) / current_price) * 100

        return {
            "moneda": SYMBOL,
            "precio_actual": round(current_price, 2),
            "prediccion_mañana": round(pred_price_final, 2),
            "tendencia": tendencia,
            "porcentaje": round(cambio_pct, 2)
        }

    except Exception as e:
        return {"error": str(e)}
