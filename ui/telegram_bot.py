"""
Telegram Bot Interactivo para PunksCode Quant Bot.

Funciones:
- Envío de mensajes (notificaciones de trades, errores)
- Recepción de comandos interactivos (/precio, /balance, /profit, /ops, /estado)
- Reporte horario automático
"""
import os
import logging
import threading
import time
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

# =====================================================
# ENVÍO DE MENSAJES
# =====================================================

def enviar_telegram(mensaje, parse_mode="Markdown"):
    """Envía un mensaje a Telegram. Compatible con el código existente."""
    if not TOKEN or not CHAT_ID:
        logger.warning("Faltan credenciales de Telegram en .env")
        return False

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": mensaje,
        "parse_mode": parse_mode,
    }

    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code != 200:
            logger.error(f"Telegram error: {response.text}")
            return False
        return True
    except Exception as e:
        logger.error(f"Error enviando a Telegram: {e}")
        return False


# =====================================================
# COMANDOS INTERACTIVOS
# =====================================================

def _cmd_precio(update_id):
    """Muestra el precio actual de BTC/USDT."""
    try:
        from core.exchange import get_price
        precio = get_price("BTCUSDT")
        enviar_telegram(
            f"📊 *Precio BTC/USDT*\n\n"
            f"💰 `${precio:,.2f}`\n"
            f"🕐 {datetime.now().strftime('%H:%M:%S')}"
        )
    except Exception as e:
        enviar_telegram(f"❌ Error obteniendo precio: {e}")


def _cmd_balance(update_id):
    """Muestra el balance actual del portafolio."""
    try:
        from ui.models import Portfolio
        wallet = Portfolio.objects.first()
        if not wallet:
            enviar_telegram("⚠️ Portafolio no inicializado.")
            return

        from core.exchange import get_price
        try:
            precio_btc = get_price("BTCUSDT")
        except Exception:
            precio_btc = 0

        val_btc = wallet.btc_balance * precio_btc
        equity = wallet.usdt_balance + val_btc
        pnl = equity - wallet.initial_capital
        pnl_pct = (pnl / wallet.initial_capital * 100) if wallet.initial_capital > 0 else 0
        signo = "+" if pnl >= 0 else ""
        icono = "🟢" if pnl >= 0 else "🔴"

        enviar_telegram(
            f"💼 *Balance del Portafolio*\n\n"
            f"💵 USDT: `${wallet.usdt_balance:,.2f}`\n"
            f"₿ BTC: `{wallet.btc_balance:.6f}` (~${val_btc:,.2f})\n"
            f"━━━━━━━━━━━━━━\n"
            f"📈 Equity Total: `${equity:,.2f}`\n"
            f"{icono} PnL: `{signo}${pnl:,.2f}` ({signo}{pnl_pct:.2f}%)\n"
            f"💰 Capital Inicial: `${wallet.initial_capital:,.2f}`"
        )
    except Exception as e:
        enviar_telegram(f"❌ Error: {e}")


def _cmd_profit(update_id):
    """Muestra resumen de ganancias/pérdidas."""
    try:
        from ui.models import Portfolio, TradeHistory, PortfolioSnapshot
        wallet = Portfolio.objects.first()
        if not wallet:
            enviar_telegram("⚠️ Portafolio no inicializado.")
            return

        from core.exchange import get_price
        try:
            precio_btc = get_price("BTCUSDT")
        except Exception:
            precio_btc = 0

        equity = wallet.usdt_balance + (wallet.btc_balance * precio_btc)
        pnl = equity - wallet.initial_capital
        roi = (pnl / wallet.initial_capital * 100) if wallet.initial_capital > 0 else 0

        # Trades totales
        total_trades = TradeHistory.objects.count()
        profit_total = sum(t.pnl_realized for t in TradeHistory.objects.all())

        # Último trade
        ultimo = TradeHistory.objects.order_by('-timestamp').first()
        ultimo_str = "Ninguno" if not ultimo else (
            f"{ultimo.strategy_used} | {ultimo.action} | "
            f"${ultimo.pnl_realized:+.2f} | {ultimo.timestamp.strftime('%d/%m %H:%M')}"
        )

        # Últimas 24h
        hace_24h = datetime.now() - timedelta(hours=24)
        trades_24h = TradeHistory.objects.filter(timestamp__gte=hace_24h)
        profit_24h = sum(t.pnl_realized for t in trades_24h)

        signo = "+" if pnl >= 0 else ""
        icono = "🟢" if pnl >= 0 else "🔴"
        signo24 = "+" if profit_24h >= 0 else ""

        enviar_telegram(
            f"📊 *Resumen de Profit*\n\n"
            f"{icono} PnL Total: `{signo}${pnl:,.2f}` ({signo}{roi:.2f}%)\n"
            f"📈 Profit Realizado: `${profit_total:+,.2f}`\n"
            f"━━━━━━━━━━━━━━\n"
            f"🔄 Trades Totales: `{total_trades}`\n"
            f"📅 Profit 24h: `{signo24}${profit_24h:,.2f}` ({trades_24h.count()} trades)\n"
            f"━━━━━━━━━━━━━━\n"
            f"🕹️ Último Trade:\n`{ultimo_str}`"
        )
    except Exception as e:
        enviar_telegram(f"❌ Error: {e}")


def _cmd_operaciones(update_id):
    """Muestra las últimas 10 operaciones."""
    try:
        from ui.models import TradeHistory
        trades = TradeHistory.objects.order_by('-timestamp')[:10]

        if not trades:
            enviar_telegram("📝 No hay operaciones registradas aún.")
            return

        lineas = []
        for t in trades:
            signo = "+" if t.pnl_realized >= 0 else ""
            icono = "🟢" if t.pnl_realized >= 0 else ("🔴" if t.pnl_realized < 0 else "⚪")
            lineas.append(
                f"{icono} `{t.timestamp.strftime('%d/%m %H:%M')}` | "
                f"{t.strategy_used} | {t.action} | `{signo}${t.pnl_realized:.2f}`"
            )

        enviar_telegram(
            f"📝 *Últimas {len(trades)} Operaciones*\n\n" +
            "\n".join(lineas)
        )
    except Exception as e:
        enviar_telegram(f"❌ Error: {e}")


def _cmd_estado(update_id):
    """Muestra el estado completo del sistema."""
    try:
        from ui.models import SystemState, Portfolio
        state = SystemState.objects.first()
        wallet = Portfolio.objects.first()

        if not state or not wallet:
            enviar_telegram("⚠️ Sistema no inicializado.")
            return

        from core.exchange import ping
        api_ok = ping()

        enviar_telegram(
            f"🤖 *Estado del Sistema*\n\n"
            f"🌐 API Binance: {'✅ Conectado' if api_ok else '❌ Desconectado'}\n"
            f"🧠 Régimen: `{state.current_regime}`\n"
            f"⚙️ Estrategia: `{state.active_strategy}`\n"
            f"━━━━━━━━━━━━━━\n"
            f"📉 Drawdown Actual: `{((wallet.usdt_balance + wallet.btc_balance) - state.peak_equity) / state.peak_equity * 100:.2f}%`\n"
            f"📉 Max Drawdown: `{state.max_drawdown:.2f}%`\n"
            f"🎯 Peak Equity: `${state.peak_equity:,.2f}`\n"
            f"━━━━━━━━━━━━━━\n"
            f"📊 ADX Límite: `{state.param_adx_max}`\n"
            f"📊 ATR Mult: `{state.param_atr_mult}`\n"
            f"🔄 Último Switch: `{state.last_switch.strftime('%d/%m %H:%M') if state.last_switch else 'N/A'}`"
        )
    except Exception as e:
        enviar_telegram(f"❌ Error: {e}")


def _cmd_ayuda(update_id):
    """Muestra los comandos disponibles."""
    enviar_telegram(
        "🤖 *Comandos Disponibles*\n\n"
        "/precio — Precio actual BTC/USDT\n"
        "/balance — Balance del portafolio\n"
        "/profit — Resumen de ganancias\n"
        "/ops — Últimas 10 operaciones\n"
        "/estado — Estado del sistema\n"
        "/ayuda — Este mensaje"
    )


# Mapa de comandos
COMANDOS = {
    "/precio": _cmd_precio,
    "/balance": _cmd_balance,
    "/profit": _cmd_profit,
    "/ops": _cmd_operaciones,
    "/operaciones": _cmd_operaciones,
    "/estado": _cmd_estado,
    "/status": _cmd_estado,
    "/ayuda": _cmd_ayuda,
    "/help": _cmd_ayuda,
    "/start": _cmd_ayuda,
}


# =====================================================
# REPORTE HORARIO AUTOMÁTICO
# =====================================================

def enviar_reporte_horario():
    """Envía un reporte de estado cada hora."""
    try:
        import django
        django.setup()
        from ui.models import Portfolio, SystemState, TradeHistory
        from core.exchange import get_price

        wallet = Portfolio.objects.first()
        state = SystemState.objects.first()

        if not wallet:
            return

        try:
            precio_btc = get_price("BTCUSDT")
        except Exception:
            precio_btc = 0

        equity = wallet.usdt_balance + (wallet.btc_balance * precio_btc)
        pnl = equity - wallet.initial_capital
        roi = (pnl / wallet.initial_capital * 100) if wallet.initial_capital > 0 else 0
        signo = "+" if pnl >= 0 else ""
        icono = "🟢" if pnl >= 0 else "🔴"

        # Trades última hora
        hace_1h = datetime.now() - timedelta(hours=1)
        trades_1h = TradeHistory.objects.filter(timestamp__gte=hace_1h)
        profit_1h = sum(t.pnl_realized for t in trades_1h)

        estrategia = state.active_strategy if state else "N/A"
        regimen = state.current_regime if state else "N/A"

        enviar_telegram(
            f"⏰ *Reporte Horario* — {datetime.now().strftime('%H:%M')}\n\n"
            f"💰 BTC: `${precio_btc:,.2f}`\n"
            f"📈 Equity: `${equity:,.2f}`\n"
            f"{icono} PnL: `{signo}${pnl:,.2f}` ({signo}{roi:.2f}%)\n"
            f"━━━━━━━━━━━━━━\n"
            f"🧠 {estrategia} ({regimen})\n"
            f"🔄 Trades última hora: `{trades_1h.count()}` (${profit_1h:+,.2f})\n"
            f"💵 USDT: `${wallet.usdt_balance:,.2f}` | ₿ `{wallet.btc_balance:.6f}`"
        )
    except Exception as e:
        logger.error(f"Error en reporte horario: {e}")


# =====================================================
# POLLING LOOP (Escucha de comandos)
# =====================================================

_polling_active = False
_last_update_id = 0

def _get_updates(offset=0):
    """Obtiene nuevos mensajes de Telegram."""
    url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
    params = {"offset": offset, "timeout": 30}
    try:
        resp = requests.get(url, params=params, timeout=35)
        if resp.status_code == 200:
            return resp.json().get("result", [])
    except Exception as e:
        logger.error(f"Error polling Telegram: {e}")
    return []


def _process_update(update):
    """Procesa un mensaje entrante."""
    global _last_update_id
    update_id = update.get("update_id", 0)
    _last_update_id = update_id + 1

    message = update.get("message", {})
    chat_id = str(message.get("chat", {}).get("id", ""))
    text = message.get("text", "").strip().lower()

    # Solo responder a nuestro chat autorizado
    if chat_id != CHAT_ID:
        logger.warning(f"Mensaje de chat no autorizado: {chat_id}")
        return

    # Buscar comando
    cmd = text.split()[0] if text else ""
    handler = COMANDOS.get(cmd)
    if handler:
        handler(update_id)
    elif text:
        enviar_telegram(
            f"🤔 Comando no reconocido: `{text}`\n\n"
            "Escribí /ayuda para ver los comandos disponibles."
        )


def start_polling():
    """Inicia el loop de polling en un thread separado."""
    global _polling_active, _last_update_id

    if not TOKEN or not CHAT_ID:
        logger.error("No se puede iniciar polling: faltan credenciales Telegram")
        return

    _polling_active = True
    logger.info("🤖 Telegram bot polling iniciado...")

    # Descartar mensajes viejos al iniciar
    updates = _get_updates(0)
    if updates:
        _last_update_id = updates[-1]["update_id"] + 1

    def _poll_loop():
        global _last_update_id
        last_report = datetime.now()

        while _polling_active:
            try:
                # Polling de comandos
                updates = _get_updates(_last_update_id)
                for update in updates:
                    _process_update(update)

                # Reporte horario
                ahora = datetime.now()
                if (ahora - last_report).total_seconds() >= 3600:
                    enviar_reporte_horario()
                    last_report = ahora

            except Exception as e:
                logger.error(f"Error en poll loop: {e}")
                time.sleep(5)

    thread = threading.Thread(target=_poll_loop, daemon=True)
    thread.start()
    return thread


def stop_polling():
    """Detiene el loop de polling."""
    global _polling_active
    _polling_active = False
