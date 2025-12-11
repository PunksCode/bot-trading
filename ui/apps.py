# ui/apps.py
from django.apps import AppConfig

class UiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ui'

    def ready(self):
        try:
            from core.price_ws import start_ws
            start_ws()
        except Exception:
            pass

