"""Resolve product image URLs: Django media + catalog /tovar/ static fallback."""

from __future__ import annotations

from pathlib import Path
from urllib.parse import quote

from django.conf import settings

from apps.core.media_urls import public_media_url

_IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".svg"}


def catalog_tovar_file(basename: str) -> Path | None:
    """Find a catalog photo by filename (case-insensitive) under CATALOG_TOVAR_DIR."""
    if not basename:
        return None
    catalog_dir = Path(settings.CATALOG_TOVAR_DIR)
    if not catalog_dir.is_dir():
        return None
    direct = catalog_dir / basename
    if direct.is_file():
        return direct
    target = basename.lower()
    for entry in catalog_dir.iterdir():
        if entry.is_file() and entry.name.lower() == target:
            return entry
    return None


def catalog_tovar_public_path(basename: str) -> str | None:
    found = catalog_tovar_file(basename)
    if not found:
        return None
    return f"/tovar/{quote(found.name)}"


def media_products_path(basename: str) -> Path:
    return Path(settings.MEDIA_ROOT) / "products" / basename


def resolve_product_image_url(file_field, request=None) -> str | None:
    """
    URL for admin/API previews.

    1. File in MEDIA_ROOT → /media/products/…
    2. Same basename in catalog tovar → /tovar/… (served by Next.js on the same host)
    """
    if not file_field or not getattr(file_field, "name", None):
        return None

    from apps.products.product_media import image_file_exists

    if image_file_exists(file_field):
        try:
            return public_media_url(file_field.url, request)
        except (ValueError, OSError):
            pass

    basename = Path(file_field.name).name
    tovar_path = catalog_tovar_public_path(basename)
    if tovar_path:
        return public_media_url(tovar_path, request)

    return None
