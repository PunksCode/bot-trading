# ui/apps.py
import sys
from django.apps import AppConfig


class UiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ui'

    def ready(self):
        # Solo iniciar WebSocket cuando corremos el servidor real,
        # NO durante management commands (migrate, check, run_telegram, etc.)
        is_server = (
            'runserver' in sys.argv or
            'daphne' in sys.argv[0] if sys.argv else False
        )
        if is_server:
            try:
                from core.core.price_ws import start_ws
                start_ws()
            except Exception:
                pass
