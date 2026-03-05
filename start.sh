#!/bin/bash
set -e

echo "🚀 Iniciando PunksCode Quant Bot en Fly.io (São Paulo)..."

# 1. Ejecutar migraciones
echo "⚙️  Ejecutando migraciones..."
python manage.py migrate --noinput

# 2. Recolectar archivos estáticos
echo "📦 Recolectando archivos estáticos..."
python manage.py collectstatic --noinput

# 3. Sincronizar balance real de Binance
echo "🔄 Sincronizando balance real de Binance..."
python manage.py sync_portfolio

# 4. Iniciar el bot de Telegram en background
echo "🤖 Iniciando bot de Telegram..."
python manage.py run_telegram &
TELEGRAM_PID=$!

# 5. Iniciar el servidor principal (Daphne ASGI con WebSocket)
echo "🌐 Iniciando servidor Daphne..."
daphne -b 0.0.0.0 -p ${PORT:-8000} bottrading.asgi:application &
DAPHNE_PID=$!

echo "✅ Bot corriendo 24/7 — Dashboard en puerto ${PORT:-8000}"

# 6. Manejar señales para shutdown limpio
cleanup() {
    echo "🛑 Apagando..."
    kill $TELEGRAM_PID $DAPHNE_PID 2>/dev/null
    wait $TELEGRAM_PID $DAPHNE_PID 2>/dev/null
    echo "👋 Adiós."
    exit 0
}
trap cleanup SIGTERM SIGINT

# 7. Esperar a que algún proceso termine
wait -n $TELEGRAM_PID $DAPHNE_PID
