"""Unified product group photo resolution for admin previews and public API."""

from __future__ import annotations

from typing import Any, TypedDict

from apps.core.media_urls import public_media_url
from apps.products.models import ProductGroup, ProductImage
from apps.products.product_media import safe_image_url
from apps.products.static_product_images import resolve_static_product_image_for_group


class GroupSiteImage(TypedDict, total=False):
    url: str
    alt: str
    source: str
    is_placeholder: bool
    image: ProductImage | None


def resolve_group_site_image(group: ProductGroup, request=None) -> GroupSiteImage:
    """
    Resolve the photo visitors see on catalog cards.

    Priority: CMS upload (ProductImage) → static catalog /tovar/ → placeholder.
    """
    img = group.images.filter(is_primary=True).first() or group.images.first()
    if img and img.image:
        url = safe_image_url(img.image, request)
        if url:
            return {
                "url": url,
                "alt": img.alt or group.name,
                "source": "cms",
                "is_placeholder": False,
                "image": img,
            }

    static_url = resolve_static_product_image_for_group(group)
    if static_url:
        return {
            "url": public_media_url(static_url, request) or static_url,
            "alt": group.name,
            "source": "static",
            "is_placeholder": True,
            "image": None,
        }

    return {
        "url": public_media_url("/placeholder-product.svg", request) or "/placeholder-product.svg",
        "alt": group.name,
        "source": "none",
        "is_placeholder": True,
        "image": None,
    }


def primary_image_payload(group: ProductGroup, request=None) -> dict[str, Any]:
    """Shape for ProductGroupListSerializer.get_primary_image."""
    data = resolve_group_site_image(group, request)
    payload: dict[str, Any] = {
        "url": data["url"],
        "alt": data["alt"],
        "is_placeholder": data.get("is_placeholder", True),
    }
    source = data.get("source")
    if source:
        payload["source"] = source
    return payload
