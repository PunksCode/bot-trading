#!/bin/bash
set -e

echo "🚀 Iniciando PunksCode Quant Bot en Render..."

# 1. Ejecutar migraciones
echo "⚙️  Ejecutando migraciones..."
python manage.py migrate --noinput

# 2. Recolectar archivos estáticos
echo "📦 Recolectando archivos estáticos..."
python manage.py collectstatic --noinput

# 3. Iniciar el bot de Telegram en background
echo "🤖 Iniciando bot de Telegram..."
python manage.py run_telegram &
TELEGRAM_PID=$!

# 4. Iniciar el servidor principal (Daphne ASGI con WebSocket)
echo "🌐 Iniciando servidor Daphne..."
daphne -b 0.0.0.0 -p ${PORT:-8000} bottrading.asgi:application &
DAPHNE_PID=$!

echo "✅ Bot corriendo — Dashboard en puerto ${PORT:-8000}"

# 5. Manejar señales para shutdown limpio
cleanup() {
    echo "🛑 Apagando..."
    kill $TELEGRAM_PID $DAPHNE_PID 2>/dev/null
    wait $TELEGRAM_PID $DAPHNE_PID 2>/dev/null
    echo "👋 Adiós."
    exit 0
}
trap cleanup SIGTERM SIGINT

# 6. Esperar a que algún proceso termine (y reiniciar si falla)
wait -n $TELEGRAM_PID $DAPHNE_PID
