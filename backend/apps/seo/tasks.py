from celery import shared_task
from celery.utils.log import get_task_logger

from .services.indexnow import submit_indexnow_urls
from .services.sitemap import write_sitemap_file

logger = get_task_logger(__name__)


@shared_task
def generate_sitemap() -> str:
    """Daily sitemap regeneration (STEP-101)."""
    path = write_sitemap_file()
    logger.info("Sitemap written to %s", path)
    return path


@shared_task
def refresh_seo_for_urls(url_paths: list[str]) -> dict:
    """Regenerate sitemap and ping IndexNow after catalog/CMS changes."""
    sitemap_path = write_sitemap_file()
    indexnow_result = submit_indexnow_urls(url_paths)
    logger.info(
        "SEO refresh: sitemap=%s indexnow=%s urls=%s",
        sitemap_path,
        indexnow_result,
        len(url_paths),
    )
    return {"sitemap": sitemap_path, "indexnow": indexnow_result, "urls": url_paths}


@shared_task
def submit_indexnow(url_paths: list[str]) -> dict:
    """Submit URLs to IndexNow only."""
    return submit_indexnow_urls(url_paths)
