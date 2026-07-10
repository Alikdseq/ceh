from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from apps.content.models import NewsPost, Page
from apps.products.models import Category, ProductGroup

from .services.urls import (
    urls_for_category,
    urls_for_news,
    urls_for_page,
    urls_for_product_group,
)


def _schedule_seo_refresh(url_paths: list[str]) -> None:
    if not url_paths:
        return
    from apps.seo.tasks import refresh_seo_for_urls

    refresh_seo_for_urls.delay(url_paths)


@receiver(post_save, sender=ProductGroup)
def product_group_saved(sender, instance, **kwargs):
    _schedule_seo_refresh(urls_for_product_group(instance))


@receiver(post_delete, sender=ProductGroup)
def product_group_deleted(sender, instance, **kwargs):
    _schedule_seo_refresh(urls_for_product_group(instance))


@receiver(post_save, sender=Category)
def category_saved(sender, instance, **kwargs):
    _schedule_seo_refresh(urls_for_category(instance))


@receiver(post_delete, sender=Category)
def category_deleted(sender, instance, **kwargs):
    _schedule_seo_refresh(urls_for_category(instance))


@receiver(post_save, sender=Page)
def page_saved(sender, instance, **kwargs):
    _schedule_seo_refresh(urls_for_page(instance))


@receiver(post_save, sender=NewsPost)
def news_saved(sender, instance, **kwargs):
    _schedule_seo_refresh(urls_for_news(instance))
