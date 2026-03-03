"""
Management command para ejecutar el Telegram Bot polling.
Uso: python manage.py run_telegram
"""
import os
import django
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Inicia el bot de Telegram con comandos interactivos y reportes horarios'

    def handle(self, *args, **options):
        from ui.telegram_bot import start_polling, enviar_telegram

        self.stdout.write(self.style.SUCCESS("🤖 Iniciando Telegram Bot..."))

        # Mensaje de inicio
        enviar_telegram(
            "🚀 *Bot Iniciado*\n\n"
            "PunksCode Quant Bot está activo.\n"
            "Escribí /ayuda para ver los comandos."
        )

        # Iniciar polling (bloqueante para este command)
        thread = start_polling()

        if thread:
            self.stdout.write(self.style.SUCCESS("✅ Telegram Bot corriendo. Ctrl+C para detener."))
            try:
                thread.join()  # Mantener el command vivo
            except KeyboardInterrupt:
                from ui.telegram_bot import stop_polling
                stop_polling()
                enviar_telegram("🔴 Bot detenido manualmente.")
                self.stdout.write(self.style.WARNING("Bot detenido."))
        else:
            self.stdout.write(self.style.ERROR("❌ No se pudo iniciar el bot. Verificá las credenciales."))
