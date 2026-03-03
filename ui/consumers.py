import json
from channels.generic.websocket import AsyncWebsocketConsumer

class DashboardConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # 1. Unirse al grupo "dashboard"
        # Esto es vital: permite que el bot le hable a este socket
        await self.channel_layer.group_add(
            "dashboard",
            self.channel_name
        )
        # 2. Aceptar la conexión
        await self.accept()
        print(f"✅ WebSocket conectado: {self.channel_name}")

    async def disconnect(self, close_code):
        # Salir del grupo al desconectar
        await self.channel_layer.group_discard(
            "dashboard",
            self.channel_name
        )
        print(f"❌ WebSocket desconectado")

    # Este método recibe los mensajes del grupo y se los manda al JS
    async def dashboard_update(self, event):
        # 'event' es lo que manda el bot. 'event["data"]' es el payload útil.
        await self.send(text_data=json.dumps(event["data"]))