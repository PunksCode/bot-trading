FROM python:3.12-slim

# Evitar que Python escriba archivos .pyc y forzar logs sin buffer
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Instalar dependencias del sistema necesarias para compilar paquetes
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el proyecto
COPY . .

# Dar permisos al script de inicio
RUN chmod +x start.sh

# Recolectar archivos estáticos para producción (requiere whitenoise)
RUN python manage.py collectstatic --noinput

EXPOSE 8000

# Usar el script de inicio que lanza Daphne + Telegram Bot
CMD ["bash", "start.sh"]
