#!/bin/bash
set -e

echo "🚀 Iniciando despliegue de PunksCode Quant Bot..."

# 1. Verificar si Docker y Docker Compose están instalados
if ! command -v docker &> /dev/null; then
    echo "❌ Docker no está instalado. Instalalo usando: sudo apt install docker.io"
    exit 1
fi

if ! command -v docker compose &> /dev/null; then
    echo "❌ Docker Compose no está instalado."
    exit 1
fi

# 2. Verificar que exista el archivo .env
if [ ! -f ".env" ]; then
    echo "❌ No se encontró el archivo .env."
    echo "Por favor copiá .env.example a .env y configurá tus claves reales."
    exit 1
fi

# 3. Crear base de datos vacía y logs si no existen para evitar que Docker cree directorios por error
touch db.sqlite3
touch bot_operaciones.log

echo "📦 Construyendo la imagen Docker..."
docker compose build

echo "⚙️  Ejecutando migraciones de base de datos..."
docker compose run --rm bot python manage.py migrate

echo "🟢 Levantando el bot en segundo plano..."
docker compose up -d

echo "✅ ¡Despliegue completado con éxito!"
echo "📄 Para ver los logs del bot, ejecutá: docker compose logs -f bot"
