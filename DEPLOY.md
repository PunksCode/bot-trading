# Guía de Despliegue en Render.com (Background Worker — 24/7)

Esta guía detalla cómo desplegar el bot de trading en Render.com usando un
Background Worker que **no se duerme nunca**, garantizando operación 24/7.

## Requisitos Previos

- Cuenta en [Render.com](https://render.com) (gratis, sin tarjeta)
- Repositorio privado en GitHub con **todo el código** (incluidos archivos core)
- Variables de entorno listas (Binance API, Telegram, Django)

## 1. Conectar GitHub con Render

1. Entrá a [dashboard.render.com](https://dashboard.render.com)
2. Hacé clic en **"New +"** → **"Blueprint"**
3. Conectá tu cuenta de GitHub si no lo hiciste
4. Seleccioná el repo **`bot-trading-original-full`** (privado)
5. Render detectará el archivo `render.yaml` y creará el servicio automáticamente

## 2. Configurar Variables de Entorno

Render pedirá que completes las variables marcadas como `sync: false`:

| Variable | Valor |
|---|---|
| `BINANCE_API_KEY` | Tu API key de Binance |
| `BINANCE_SECRET_KEY` | Tu secret key de Binance |
| `BINANCE_BASE_URL` | `https://api.binance.com` (producción) |
| `BINANCE_WS_URL` | `wss://stream.binance.com:9443` (producción) |
| `TELEGRAM_TOKEN` | Token de tu bot de Telegram |
| `TELEGRAM_CHAT_ID` | Tu chat ID de Telegram |

Las demás variables (`DJANGO_SECRET_KEY`, etc.) se configuran automáticamente.

## 3. Deploy

Render construirá la imagen Docker y levantará el bot automáticamente.
El bot ejecuta:
- **Daphne ASGI** (servidor web + WebSocket)
- **Bot de Telegram** (comandos interactivos + reportes horarios)

## 4. Seguridad (IP de Binance)

Una vez desplegado:
1. En el panel de Render, buscá la IP saliente del servicio
2. En Binance → API Management → Restringir a IPs de confianza
3. Pegá la IP de Render

## Comandos Útiles

- **Ver logs:** Panel de Render → tu servicio → Logs
- **Reiniciar:** Panel de Render → tu servicio → Manual Deploy
- **Actualizar:** Push a GitHub → Render re-deploya automáticamente

## Arquitectura

```
┌─────────────────────────────────────┐
│   Render Background Worker (Free)   │
│                                     │
│   ┌──────────┐   ┌──────────────┐   │
│   │  Daphne  │   │   Telegram   │   │
│   │  (ASGI)  │   │     Bot      │   │
│   └────┬─────┘   └──────┬───────┘   │
│        │                 │           │
│   Dashboard Web    Comandos/Reportes │
│   + WebSocket      + Alertas         │
└────────┬─────────────────┬───────────┘
         │                 │
    ┌────▼────┐      ┌─────▼────┐
    │ Binance │      │ Telegram │
    │   API   │      │   API    │
    └─────────┘      └──────────┘
```
