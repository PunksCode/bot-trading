import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import ui.routing

# Asegúrate de que esto coincida con el nombre de tu carpeta de configuración
# En tu settings.py decía "bottrading.settings", así que usamos "bottrading"
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bottrading.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            ui.routing.websocket_urlpatterns
        )
    ),
})