from celery import Celery
from app.core.config import get_settings

settings = get_settings()

celery_app = Celery("lead_hunter", broker=settings.redis_url, backend=settings.redis_url, include=["app.workers.tasks"])
celery_app.set_default()
celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    task_always_eager=settings.celery_task_always_eager,
    task_eager_propagates=True,
    beat_schedule={
        "discover-leads-every-interval": {
            "task": "app.workers.tasks.run_active_campaigns",
            "schedule": settings.lead_search_interval_minutes * 60,
        },
        "process-failed-jobs": {
            "task": "app.workers.tasks.handle_failed_jobs",
            "schedule": 300,
        },
    },
)
