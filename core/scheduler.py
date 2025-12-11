import os
from apscheduler.schedulers.background import BackgroundScheduler
from django.utils import timezone
from dotenv import load_dotenv
from .executor import execute_signal
from ui.models import StrategyConfig, Trade

load_dotenv()
SYMBOL = os.getenv("SYMBOL", "SOLUSDT")
TRADE_QTY = float(os.getenv("TRADE_QTY", "0.1"))

sched = BackgroundScheduler()

def tick():
    # Placeholder para nueva lógica basada en IA
    pass

def start():
    if not sched.running:
        sched.add_job(tick, "interval", seconds=60, next_run_time=timezone.now())
        sched.start()

def stop():
    if sched.running:
        sched.shutdown(wait=False)
