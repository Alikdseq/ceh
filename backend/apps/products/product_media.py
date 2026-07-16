"""Product media on disk — shared checks (admin, API, management commands)."""

from __future__ import annotations

from django.core.files.storage import default_storage

from apps.products.models import ProductGroup, ProductImage


def image_file_exists(file_field) -> bool:
    if not file_field or not file_field.name:
        return False
    try:
        return default_storage.exists(file_field.name)
    except OSError:
        return False


def safe_image_url(file_field) -> str | None:
    if not image_file_exists(file_field):
        return None
    try:
        return file_field.url
    except (ValueError, OSError):
        return None


def prune_broken_images_for_group(group: ProductGroup) -> int:
    """Delete ProductImage rows whose files are missing (DB orphan after redeploy)."""
    removed = 0
    for img in list(group.images.all()):
        if img.image.name and not image_file_exists(img.image):
            img.delete()
            removed += 1
    return removed


def prune_all_broken_product_images() -> int:
    removed = 0
    for img in ProductImage.objects.select_related("group").iterator():
        if img.image.name and not image_file_exists(img.image):
            img.delete()
            removed += 1
    return removed
