from datetime import timedelta
import os
from celery import Celery

redis_url = os.getenv("REDIS_URL", "redis://redis_container:6379")

celery_app = Celery(__name__, broker=redis_url, backend=redis_url, include=['tasks'])

celery_app.conf.beat_schedule = {
    "generate_user_report": {
        "task": "tasks.generate_user_report",
        "schedule": timedelta(seconds=10),  # Every 30 minutes
    },
}
celery_app.conf.timezone = "Asia/Bishkek"
celery_app.autodiscover_tasks()
