import secrets
from datetime import timedelta
from decimal import Decimal

from django.core.cache import cache
from django.db import transaction
from django.utils import timezone

from apps.products.models import ProductVariant

from ..models import QuoteCart, QuoteCartItem

CART_COOKIE = "cart_session"
CART_HEADER = "X-Cart-Session"
CART_CACHE_PREFIX = "cart:session:"
CART_TTL_DAYS = 30
CART_CACHE_TTL = CART_TTL_DAYS * 24 * 3600


def new_session_key() -> str:
    return secrets.token_urlsafe(32)


def resolve_session_key(request) -> tuple[str, bool]:
    """Return (session_key, is_new)."""
    key = request.COOKIES.get(CART_COOKIE) or request.headers.get(CART_HEADER, "").strip()
    if key:
        return key, False
    return new_session_key(), True


def _cache_key(session_key: str) -> str:
    return f"{CART_CACHE_PREFIX}{session_key}"


def _touch_cache(cart: QuoteCart) -> None:
    cache.set(_cache_key(cart.session_key), cart.pk, timeout=CART_CACHE_TTL)


def get_or_create_cart(session_key: str, user=None) -> QuoteCart:
    now = timezone.now()
    cached_id = cache.get(_cache_key(session_key))
    if cached_id:
        cart = (
            QuoteCart.objects.filter(pk=cached_id, expires_at__gt=now)
            .prefetch_related("items__variant__group")
            .first()
        )
        if cart:
            _touch_cache(cart)
            return cart

    cart = (
        QuoteCart.objects.filter(session_key=session_key, expires_at__gt=now)
        .prefetch_related("items__variant__group")
        .first()
    )
    if cart:
        _touch_cache(cart)
        return cart

    expires = now + timedelta(days=CART_TTL_DAYS)
    cart = QuoteCart.objects.create(session_key=session_key, user=user, expires_at=expires)
    _touch_cache(cart)
    return cart


def get_cart_queryset(cart: QuoteCart):
    return cart.items.select_related(
        "variant", "variant__group", "variant__group__category",
    ).order_by("id")


def cart_subtotal(cart: QuoteCart) -> Decimal:
    return sum((item.line_total for item in cart.items.all()), Decimal("0"))


def serialize_cart(cart: QuoteCart, request) -> dict:
    items = []
    for item in get_cart_queryset(cart):
        variant = item.variant
        group = variant.group
        image = group.images.filter(is_primary=True).first() or group.images.first()
        image_url = None
        if image and image.image:
            image_url = request.build_absolute_uri(image.image.url)
        items.append({
            "id": item.pk,
            "variant_id": variant.pk,
            "sku_code": variant.sku_code,
            "product_name": group.name,
            "product_slug": group.slug,
            "category_slug": group.category.slug if group.category_id else "",
            "quantity": item.quantity,
            "unit_price": str(item.unit_price_snapshot),
            "line_total": str(item.line_total),
            "image_url": image_url,
            "coil_voltage_v": item.coil_voltage_snapshot,
        })
    subtotal = cart_subtotal(cart)
    return {
        "items": items,
        "item_count": sum(i.quantity for i in cart.items.all()),
        "subtotal": str(subtotal),
        "vat_included": True,
    }


def attach_session(response, session_key: str, is_new: bool) -> None:
    if is_new or session_key:
        response.set_cookie(
            CART_COOKIE,
            session_key,
            max_age=CART_CACHE_TTL,
            httponly=True,
            samesite="Lax",
            secure=False,
        )
        response["X-Cart-Session"] = session_key


@transaction.atomic
def add_item(cart: QuoteCart, variant_id: int, quantity: int = 1) -> QuoteCartItem:
    variant = (
        ProductVariant.objects.select_related("group")
        .filter(pk=variant_id, is_active=True, group__is_active=True)
        .first()
    )
    if not variant:
        raise ValueError("variant_not_found")

    quantity = max(1, min(9999, quantity))
    item, created = QuoteCartItem.objects.get_or_create(
        cart=cart,
        variant=variant,
        defaults={
            "quantity": quantity,
            "unit_price_snapshot": variant.price,
            "coil_voltage_snapshot": variant.coil_voltage_v,
        },
    )
    if not created:
        item.quantity = min(9999, item.quantity + quantity)
        item.save(update_fields=["quantity"])
    cart.updated_at = timezone.now()
    cart.save(update_fields=["updated_at"])
    _touch_cache(cart)
    return item


@transaction.atomic
def update_item(cart: QuoteCart, item_id: int, quantity: int) -> QuoteCartItem | None:
    item = QuoteCartItem.objects.filter(cart=cart, pk=item_id).first()
    if not item:
        return None
    if quantity <= 0:
        item.delete()
        return None
    item.quantity = min(9999, quantity)
    item.save(update_fields=["quantity"])
    _touch_cache(cart)
    return item


@transaction.atomic
def remove_item(cart: QuoteCart, item_id: int) -> bool:
    deleted, _ = QuoteCartItem.objects.filter(cart=cart, pk=item_id).delete()
    if deleted:
        _touch_cache(cart)
    return bool(deleted)


@transaction.atomic
def clear_cart(cart: QuoteCart) -> None:
    cart.items.all().delete()
    _touch_cache(cart)
