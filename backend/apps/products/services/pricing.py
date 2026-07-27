"""Price propagation and queryset helpers for catalog variants."""

from __future__ import annotations

from django.db.models import Min, Q, QuerySet

from apps.products.models import ProductGroup, ProductVariant

ACTIVE_PRICED_VARIANT_FILTER = Q(variants__is_active=True, variants__price__gt=0)


def annotate_min_price(queryset: QuerySet[ProductGroup]) -> QuerySet[ProductGroup]:
    """Minimum positive variant price for list/detail serializers."""
    return queryset.annotate(min_price=Min("variants__price", filter=ACTIVE_PRICED_VARIANT_FILTER))


def propagate_prices_within_groups() -> int:
    """Copy a group's reference price to sibling variants with price=0."""
    updated = 0
    for group in ProductGroup.objects.filter(is_active=True, variants__price=0).distinct():
        ref = (
            group.variants.filter(is_active=True, price__gt=0)
            .order_by("-is_default", "pk")
            .first()
        )
        if not ref:
            continue
        updated += group.variants.filter(is_active=True, price=0).update(
            price=ref.price,
            price_valid_from=ref.price_valid_from,
        )
    return updated


def propagate_prices_by_sku_prefix() -> int:
    """Apply base SKU price to coil/aux suffix variants (КТ6012Б-У3-220V)."""
    updated = 0
    for variant in ProductVariant.objects.filter(is_active=True, price__gt=0).iterator():
        updated += ProductVariant.objects.filter(
            is_active=True,
            sku_code__startswith=f"{variant.sku_code}-",
            price=0,
        ).update(price=variant.price, price_valid_from=variant.price_valid_from)
    return updated


def sync_all_variant_prices() -> dict[str, int]:
    """Run all propagation strategies after pricelist or catalog import."""
    within = propagate_prices_within_groups()
    prefix = propagate_prices_by_sku_prefix()
    within_after = propagate_prices_within_groups()
    return {
        "within_group": within + within_after,
        "by_sku_prefix": prefix,
    }


def apply_group_price(group: ProductGroup, price, price_valid_from) -> int:
    """Set the same pricelist price on every active variant in a product group."""
    return group.variants.filter(is_active=True).update(
        price=price,
        price_valid_from=price_valid_from,
    )
