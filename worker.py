import os
from celery import Celery


REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")


celery_app = Celery(
    "influenza_classifier",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["app.tasks"]
)


celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    result_expires=3600,
    task_track_started=True,
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    broker_connection_retry_on_startup=True
)

if __name__ == "__main__":
    celery_app.start()
