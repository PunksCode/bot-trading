"""
Management command: sync_portfolio
Lee el balance real de Binance y actualiza la DB local (Portfolio + SystemState).
Se ejecuta al arrancar el bot en producción.
"""
import logging
from django.core.management.base import BaseCommand
from core.exchange import get_balances, get_price
from ui.models import Portfolio, SystemState

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Sincroniza el Portfolio con los balances reales de Binance'

    def handle(self, *args, **options):
        self.stdout.write("🔄 Sincronizando con Binance...")

        balances = get_balances()
        if 'error' in balances:
            self.stderr.write(f"❌ Error al leer balances: {balances['error']}")
            return

        usdt = balances['USDT']
        btc = balances['BTC']

        # Obtener precio actual de BTC para calcular equity
        try:
            btc_price = get_price('BTCUSDT')
        except Exception as e:
            self.stderr.write(f"❌ Error al obtener precio: {e}")
            return

        equity = usdt + (btc * btc_price)

        # Crear o actualizar Portfolio
        wallet, created = Portfolio.objects.get_or_create(id=1)

        if created:
            # Primera vez: el capital inicial ES el balance real actual
            wallet.initial_capital = equity

        wallet.usdt_balance = usdt
        wallet.btc_balance = btc
        wallet.save()

        # Actualizar peak_equity en SystemState
        state, _ = SystemState.objects.get_or_create(id=1)
        if equity > state.peak_equity or state.peak_equity == 10000.0:
            state.peak_equity = equity
        state.save()

        self.stdout.write(
            f"✅ Portfolio sincronizado:\n"
            f"   💵 USDT: {usdt:,.2f}\n"
            f"   ₿  BTC:  {btc:.8f}\n"
            f"   💰 Equity: ${equity:,.2f}\n"
            f"   📊 Capital Inicial: ${wallet.initial_capital:,.2f}"
        )
