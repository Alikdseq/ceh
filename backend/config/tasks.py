from celery import shared_task
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


@shared_task(bind=True, ignore_result=True)
def debug_task(self):
    """Ping task for Celery health check (STEP-036)."""
    logger.info("Celery debug_task ping: request=%s", self.request.id)
    return "pong"
