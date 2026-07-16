"""Product media on disk — shared checks (admin, API, management commands)."""

from __future__ import annotations

from pathlib import Path

from django.core.files.storage import default_storage

from apps.products.catalog_static_photos import catalog_tovar_file, resolve_product_image_url
from apps.products.models import ProductGroup, ProductImage


def image_file_exists(file_field) -> bool:
    if not file_field or not file_field.name:
        return False
    try:
        return default_storage.exists(file_field.name)
    except OSError:
        return False


def safe_image_url(file_field, request=None) -> str | None:
    return resolve_product_image_url(file_field, request)


def _orphan_product_image(file_field) -> bool:
    """True when neither media storage nor catalog /tovar/ can serve this record."""
    if not file_field or not file_field.name:
        return True
    if image_file_exists(file_field):
        return False
    return catalog_tovar_file(Path(file_field.name).name) is None


def prune_broken_images_for_group(group: ProductGroup) -> int:
    """Delete ProductImage rows with no media file and no catalog /tovar/ fallback."""
    removed = 0
    for img in list(group.images.all()):
        if _orphan_product_image(img.image):
            img.delete()
            removed += 1
    if removed and getattr(group, "_prefetched_objects_cache", None):
        group._prefetched_objects_cache.pop("images", None)
    return removed


def prune_all_broken_product_images() -> int:
    removed = 0
    for img in ProductImage.objects.select_related("group").iterator():
        if _orphan_product_image(img.image):
            img.delete()
            removed += 1
    return removed


def product_group_ids_with_broken_images() -> list[int]:
    """Product groups with at least one orphan image (no media file, no catalog fallback)."""
    ids: set[int] = set()
    for img in ProductImage.objects.only("group_id", "image").iterator():
        if _orphan_product_image(img.image):
            ids.add(img.group_id)
    return sorted(ids)
