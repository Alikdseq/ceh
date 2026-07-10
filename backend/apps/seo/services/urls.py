"""Collect public frontend URLs for SEO refresh tasks."""

from apps.content.models import NewsPost, Page
from apps.products.models import Category, ProductGroup
from apps.products.utils import category_path_slugs, product_catalog_path

PAGE_SLUG_PATHS = {
    "about": "/about/",
    "contacts": "/contacts/",
    "privacy": "/privacy/",
    "terms": "/terms/",
    "support": "/support/",
    "dealers": "/dealers/",
    "about-production": "/about/production/",
    "about-certificates": "/about/certificates/",
}


def category_url_path(category) -> str:
    slugs = category_path_slugs(category)
    return f"/catalog/{'/'.join(slugs)}/"


def urls_for_product_group(group: ProductGroup) -> list[str]:
    if not group.is_active:
        return []
    return [product_catalog_path(group)]


def urls_for_category(category: Category) -> list[str]:
    if not category.is_active:
        return []
    paths = [category_url_path(category)]
    for group in ProductGroup.objects.filter(category=category, is_active=True):
        paths.append(product_catalog_path(group))
    return paths


def urls_for_page(page: Page) -> list[str]:
    if not page.is_published:
        return []
    path = PAGE_SLUG_PATHS.get(page.slug, f"/pages/{page.slug}/")
    return [path if path.endswith("/") else f"{path}/"]


def urls_for_news(post: NewsPost) -> list[str]:
    if not post.is_published:
        return []
    return [f"/news/{post.slug}/"]
