# Guía de Despliegue en Fly.io (São Paulo — 24/7)

Despliegue del bot de trading en **Fly.io** con VM always-on en la región
**São Paulo (GRU)** — sin bloqueo de Binance, sin dormirse nunca.

## Requisitos Previos

- Cuenta en [Fly.io](https://fly.io) (registrarse con GitHub)
- Repositorio privado en GitHub con todo el código
- Variables de entorno listas (Binance API, Telegram, Django)

## 1. Instalar flyctl

```bash
curl -L https://fly.io/install.sh | sh
```

Agregar al PATH (si no se agrega automáticamente):
```bash
export FLYCTL_INSTALL="/home/$USER/.fly"
export PATH="$FLYCTL_INSTALL/bin:$PATH"
```

## 2. Login

```bash
fly auth login
```

Se abrirá el navegador para autenticarte con GitHub.

## 3. Lanzar la App

Desde el directorio del proyecto:

```bash
fly launch --no-deploy
```

- Seleccioná la región **São Paulo (GRU)**
- Fly detectará el `Dockerfile` y `fly.toml` automáticamente
- Usá `--no-deploy` para configurar secrets antes del primer deploy

## 4. Configurar Variables de Entorno (Secrets)

```bash
fly secrets set \
  BINANCE_API_KEY="tu_api_key" \
  BINANCE_SECRET_KEY="tu_secret_key" \
  BINANCE_BASE_URL="https://api.binance.com" \
  BINANCE_WS_URL="wss://stream.binance.com:9443" \
  TELEGRAM_TOKEN="tu_token" \
  TELEGRAM_CHAT_ID="tu_chat_id" \
  DJANGO_SECRET_KEY="una-clave-secreta-larga-y-aleatoria" \
  DJANGO_DEBUG="False" \
  DJANGO_ALLOWED_HOSTS="*" \
  SYMBOL="BTCUSDT"
```

## 5. Deploy

```bash
fly deploy
```

Fly construirá la imagen Docker y levantará el bot automáticamente.

## 6. Verificar

```bash
# Ver logs en tiempo real
fly logs

# Estado de la máquina
fly status

# Acceder por SSH
fly ssh console

# Health check manual
fly ssh console -C "curl localhost:8000/health"
```

## Configuración Always-On

El archivo `fly.toml` ya tiene configurado:

```toml
auto_stop_machines = "off"     # NO se detiene
min_machines_running = 1       # Siempre al menos 1 corriendo
```

**Tu bot corre 24/7 sin dormirse.**

## Arquitectura

```
┌─────────────────────────────────────────┐
│   Fly.io VM — São Paulo (GRU)           │
│   shared-cpu-1x • 256 MB • Always-On    │
│                                         │
│   ┌──────────┐   ┌──────────────┐       │
│   │  Daphne  │   │   Telegram   │       │
│   │  (ASGI)  │   │     Bot      │       │
│   └────┬─────┘   └──────┬───────┘       │
│        │                 │               │
│   Dashboard Web    Comandos/Reportes     │
│   + WebSocket      + Alertas             │
└────────┬─────────────────┬───────────────┘
         │                 │
    ┌────▼────┐      ┌─────▼────┐
    │ Binance │      │ Telegram │
    │   API   │      │   API    │
    └─────────┘      └──────────┘
```

## Comandos Útiles

| Comando | Descripción |
|---------|-------------|
| `fly logs` | Ver logs en tiempo real |
| `fly status` | Estado de la app/máquinas |
| `fly deploy` | Re-deployar con últimos cambios |
| `fly ssh console` | Acceder a la VM por SSH |
| `fly secrets list` | Ver secrets configurados |
| `fly scale show` | Ver recursos asignados |
