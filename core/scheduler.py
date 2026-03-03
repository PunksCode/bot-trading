import os
from apscheduler.schedulers.background import BackgroundScheduler
from django.utils import timezone
from dotenv import load_dotenv

load_dotenv()
SYMBOL = os.getenv("SYMBOL", "BTCUSDT")

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
