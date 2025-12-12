# AI Quantitative Trading Bot

Este repositorio aloja el desarrollo de un sistema de trading algorítmico autónomo que ha evolucionado desde estrategias lineales básicas hasta el uso de Redes Neuronales Recurrentes (LSTM) para la predicción de activos financieros en tiempo real.

## 🏗 Arquitectura del Sistema

El proyecto se ejecuta sobre una infraestructura moderna optimizada para Deep Learning:

* **Entorno:** Linux (Ubuntu sobre WSL2) para gestión eficiente de dependencias.
* **Procesamiento:** Entrenamiento acelerado por hardware mediante **NVIDIA CUDA (GPU RTX 2060)**.
* **Backend:** Python 3.12 + Django (API REST y gestión de datos).
* **Frontend:** Dashboard interactivo con integración de gráficos TradingView.
* **Data Feed:** Conexión directa a Exchange (Binance) vía `ccxt`.

## 📈 Evolución del Proyecto

### Fase 1: Algoritmia Lineal (Legacy)
El proyecto inició como un bot de reglas estáticas (similar a estrategias Grid/DCA).
* **Limitación:** Incapacidad de adaptación a cambios de tendencia o volatilidad extrema.
* **Estado:** Deprecado en favor de modelos probabilísticos.

### Fase 2: Introducción al Deep Learning (LSTM V1)
Implementación de la primera Red Neuronal Recurrente (Long Short-Term Memory).
* **Input:** Series temporales de precios de cierre (Diario).
* **Infraestructura:** Windows nativo (limitado por conflictos de dependencias TensorFlow/Numpy).
* **Resultado:** Capacidad de predecir tendencias simples, pero con baja sensibilidad al ruido del mercado.

### Fase 3: Migración y Feature Engineering (LSTM V2)
Refactorización completa del entorno a Linux y enriquecimiento de datos.
* **Features:** Incorporación de análisis técnico multivariable:
    * **RSI (Relative Strength Index):** Detección de zonas de sobrecompra/sobreventa.
    * **Bandas de Bollinger:** Medición de volatilidad dinámica.
* **Mejora:** El modelo dejó de ser "ciego" al contexto técnico, reduciendo falsos positivos en tendencias fuertes.

### Fase 4: Intradía y Paper Trading (Estado Actual - V3)
Escalado hacia operaciones de alta frecuencia y simulación financiera.
* **Timeframe:** Reducción de velas diarias a **15 minutos** para operativa Intradía.
* **Data Source:** Migración de Yahoo Finance a **Binance API (ccxt)** para precisión de nivel Exchange.
* **Paper Trading:** Sistema de billetera virtual y registro de transacciones para validación de estrategias sin riesgo de capital (`Portfolio` & `Trade` models).

## 🚀 Roadmap y Próximos Pasos

El desarrollo actual se centra en aumentar la dimensionalidad de los datos de entrada:

1.  **Análisis de Volumen:** Incorporación de indicadores de flujo de dinero (OBV, Volume Profile) para confirmar rupturas de precio.
2.  **Level 2 Data (Order Book):** Análisis de la profundidad de mercado para detectar muros de compra/venta institucionales.
3.  **Live Trading:** Ejecución de órdenes reales vía API privada.

## 🛠 Instalación y Despliegue

1.  Clonar el repositorio.
2.  Iniciar entorno virtual: `source venv/bin/activate`
3.  Instalar dependencias: `pip install -r requirements.txt`
4.  Ejecutar servidor: `python manage.py runserver`

---
*Desarrollado por PunksCode.*