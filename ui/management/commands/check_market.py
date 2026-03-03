from django.core.management.base import BaseCommand
from ui.trader import ejecutar_sistema
from ui.models import Portfolio, PortfolioSnapshot # <--- IMPORTANTE: Importar el snapshot
import ccxt
import pandas as pd
from datetime import datetime

# Intentamos importar Telegram, si falla no rompe el bot
try:
    from ui.telegram_bot import enviar_telegram
    TELEGRAM_ACTIVO = True
except ImportError:
    TELEGRAM_ACTIVO = False

class Command(BaseCommand):
    help = 'Ejecuta un ciclo de análisis, guarda historial y notifica'

    def handle(self, *args, **options):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.stdout.write(f"[{now}] 💓 Iniciando chequeo...")

        try:
            exchange = ccxt.binance()
            ohlcv = exchange.fetch_ohlcv('BTC/USDT', '4h', limit=200)
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            
            if df.empty: return

            precio_actual = df.iloc[-1]['close']
            
            # 1. EJECUTAR CEREBRO (Operativa)
            resultado = ejecutar_sistema(df, precio_actual)
            
            # 2. CALCULAR DATOS FINANCIEROS
            wallet = Portfolio.objects.first() 
            equity_actual = resultado['equity']
            capital_inicial = wallet.initial_capital
            
            pnl_dolares = equity_actual - capital_inicial
            roi_porcentaje = (pnl_dolares / capital_inicial) * 100 if capital_inicial > 0 else 0
            
            # 3. GUARDAR HISTORIAL (Persistencia - Lo que dijo la otra IA)
            # Esto permite graficar la curva de dinero después
            PortfolioSnapshot.objects.create(
                equity=equity_actual,
                pnl_usd=pnl_dolares,
                pnl_percent=roi_porcentaje,
                strategy_used=resultado['strategy']
            )

            # 4. REPORTAR A LOG
            signo = "+" if pnl_dolares >= 0 else ""
            color = self.style.SUCCESS if pnl_dolares >= 0 else self.style.ERROR
            
            self.stdout.write(self.style.SUCCESS(f"✅ CICLO COMPLETADO Y GUARDADO"))
            self.stdout.write(f"   Estrategia: {resultado['strategy']}")
            self.stdout.write(f"   Equity: ${equity_actual:.2f}")
            self.stdout.write(color(f"   PnL: {signo}${pnl_dolares:.2f} ({signo}{roi_porcentaje:.2f}%)"))

            # 5. ENVIAR A TELEGRAM (Notificación)
            if TELEGRAM_ACTIVO:
                icono = "🟢" if pnl_dolares >= 0 else "🔴"
                msg = (
                    f"🤖 **REPORTE CICLO**\n"
                    f"🧠 {resultado['strategy']} ({resultado['regime']})\n"
                    f"💰 Eq: ${equity_actual:.2f}\n"
                    f"{icono} PnL: {signo}${pnl_dolares:.2f} ({signo}{roi_porcentaje:.2f}%)"
                )
                enviar_telegram(msg)
                self.stdout.write("📨 Telegram enviado.")

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ ERROR: {str(e)}"))
            if TELEGRAM_ACTIVO:
                enviar_telegram(f"❌ ERROR BOT: {str(e)}")
