# ui/bot_runtime.py

"""
Estado en memoria del bot.
NO persiste.
NO toca trading.
Seguro para desarrollo.
"""

BOT_STATE = {
    "last_update": None,
    "tendencia": None,
    "precio_actual": None,
    "prediccion": None,
    "mensaje": None,
}
