"""Shared catalog path helpers for API and SEO sitemap."""

import logging

from django.conf import settings
from django.core.cache import cache

from .models import Category

logger = logging.getLogger(__name__)

CATEGORIES_CACHE_KEY = "api:categories:tree"
PUBLIC_CATEGORY_IDS_CACHE_KEY = "api:categories:public_ids"
CATEGORIES_CACHE_TTL = getattr(settings, "CACHE_TTL_CATEGORIES", 3600)

# Не отдаём в публичное API / не показываем в таблице характеристик
PUBLIC_HIDDEN_SPEC_KEYS = frozenset({"application_category"})


def category_path_slugs(category) -> list[str]:
    """Return MPTT slug path from root to category (inclusive)."""
    return [a.slug for a in category.get_ancestors(include_self=True)]


def product_catalog_path(group) -> str:
    """Return frontend catalog path for a product group, e.g. /catalog/a/b/product-slug/."""
    slugs = category_path_slugs(group.category)
    product_slug = (group.slug or "").strip()
    if not product_slug:
        from django.utils.text import slugify

        product_slug = slugify(group.name or f"group-{group.pk}", allow_unicode=True)[:255]
    return f"/catalog/{'/'.join([*slugs, product_slug])}/"


def is_category_public(category) -> bool:
    """Category is visible on site when active and all ancestors are active."""
    if not category.is_active:
        return False
    return not category.get_ancestors().filter(is_active=False).exists()


def _public_category_ids_queryset() -> list[int]:
    return [cat.id for cat in Category.objects.filter(is_active=True) if is_category_public(cat)]


def get_public_category_ids() -> list[int]:
    """Cached list of category IDs visible on the public site."""
    if settings.DEBUG:
        return _public_category_ids_queryset()

    cached = cache.get(PUBLIC_CATEGORY_IDS_CACHE_KEY)
    if cached is not None:
        return cached

    ids = _public_category_ids_queryset()
    cache.set(PUBLIC_CATEGORY_IDS_CACHE_KEY, ids, CATEGORIES_CACHE_TTL)
    return ids


def invalidate_catalog_cache() -> None:
    try:
        cache.delete(CATEGORIES_CACHE_KEY)
        cache.delete(PUBLIC_CATEGORY_IDS_CACHE_KEY)
    except Exception:
        logger.warning("Catalog cache invalidation skipped", exc_info=True)
