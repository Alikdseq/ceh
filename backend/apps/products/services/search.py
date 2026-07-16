"""PostgreSQL trigram search helpers (STEP-035)."""
from __future__ import annotations

import re

from django.contrib.postgres.search import TrigramSimilarity
from django.db.models import Case, IntegerField, Q, QuerySet, Value, When
from django.db.models.functions import Greatest
from django.utils.html import strip_tags

from apps.products.models import ProductGroup, ProductVariant
from apps.products.utils import get_public_category_ids

from .catalog_query_parse import parse_product_query

# Short catalog tokens → product_type (exact match for 2–3 char queries like «КТ»).
PRODUCT_TYPE_QUERY_ALIASES: dict[str, str] = {
    "кт": ProductGroup.ProductType.KT,
    "kt": ProductGroup.ProductType.KT,
    "ктп": ProductGroup.ProductType.KTP,
    "ktp": ProductGroup.ProductType.KTP,
    "ктэ": ProductGroup.ProductType.KTE,
    "kte": ProductGroup.ProductType.KTE,
}


def normalize_search_query(raw: str) -> str:
    """Normalize user query: lowercase, strip spaces/dashes."""
    return raw.strip().lower().replace(" ", "").replace("-", "")


def _search_terms(raw: str, normalized: str) -> list[str]:
    """Distinct non-empty search terms (with and without spaces)."""
    terms: list[str] = []
    for term in (raw.strip(), normalized):
        if term and term not in terms:
            terms.append(term)
    return terms


def build_group_search_text(group: ProductGroup) -> str:
    category_name = ""
    if group.category_id:
        category_name = group.category.name

    parts = [
        group.name,
        group.short_description,
        strip_tags(group.full_description) if group.full_description else "",
        category_name,
        group.series_code,
        group.slug.replace("-", " "),
        group.product_type,
        group.get_product_type_display(),
    ]
    if group.nominal_current_a:
        parts.append(f"{group.nominal_current_a}a")
        parts.append(f"{group.nominal_current_a}а")
    for series in set(re.findall(r"\d{4}", group.name or "")) | ({group.series_code} if group.series_code else set()):
        if not series:
            continue
        for prefix in ("kt", "кт", "ktp", "ктп"):
            parts.extend(
                [
                    f"{prefix}{series}",
                    f"{prefix} {series}",
                    f"{prefix}-{series}",
                    f"{prefix}{series}b",
                    f"{prefix}{series}bs",
                    f"{prefix}{series}s",
                ]
            )
        parts.append(series)
    for variant in group.variants.filter(is_active=True).only("sku_code", "execution")[:12]:
        parts.append(variant.sku_code)
        parts.append(variant.sku_code.replace("-", ""))
    return " ".join(p for p in parts if p).lower()


def build_variant_search_text(variant: ProductVariant) -> str:
    sku = variant.sku_code.lower().replace("-", "")
    parts = [
        variant.sku_code,
        sku,
        variant.slug.replace("-", " "),
        variant.get_execution_display(),
        variant.aux_contacts,
    ]
    return " ".join(p for p in parts if p).lower()


def rebuild_all_search_indexes() -> tuple[int, int]:
    """Populate search_vector fields for groups and variants."""
    groups_updated = 0
    for group in ProductGroup.objects.select_related("category").iterator():
        text = build_group_search_text(group)
        if group.search_vector != text:
            ProductGroup.objects.filter(pk=group.pk).update(search_vector=text)
            groups_updated += 1

    variants_updated = 0
    for variant in ProductVariant.objects.select_related("group", "group__category").iterator():
        text = f"{build_variant_search_text(variant)} {build_group_search_text(variant.group)}"
        if variant.search_vector != text:
            ProductVariant.objects.filter(pk=variant.pk).update(search_vector=text)
            variants_updated += 1

    return groups_updated, variants_updated


def _build_direct_match_q(raw: str, normalized: str) -> Q:
    """Case-insensitive matches on catalog fields (never match empty digit/sku patterns)."""
    product_type = PRODUCT_TYPE_QUERY_ALIASES.get(normalized)
    is_short_type_query = product_type is not None and len(normalized) <= 3

    if is_short_type_query:
        direct = Q(product_type=product_type)
    else:
        direct = Q()
        for term in _search_terms(raw, normalized):
            direct |= Q(name__icontains=term)
            direct |= Q(short_description__icontains=term)
            direct |= Q(category__name__icontains=term)
            direct |= Q(search_vector__icontains=term)
            direct |= Q(variants__search_vector__icontains=term)

    digits = re.sub(r"\D", "", raw)
    if digits and len(digits) >= 4:
        direct |= Q(series_code=digits[-4:])
        if len(digits) > 4:
            direct |= Q(series_code__icontains=digits)

    parsed = parse_product_query(raw)
    if parsed:
        direct |= Q(series_code=parsed.series_code)
        if parsed.product_type:
            direct |= Q(product_type=parsed.product_type)

    sku_query = raw.replace(" ", "").replace("-", "")
    if sku_query:
        direct |= Q(variants__sku_code__icontains=sku_query)

    return direct


def _annotate_relevance(qs: QuerySet[ProductGroup], raw: str, normalized: str) -> QuerySet[ProductGroup]:
    """Prefer exact SKU and name matches over broad category hits."""
    sku_query = raw.replace(" ", "").replace("-", "")
    whens = [
        When(variants__sku_code__iexact=sku_query, then=Value(100)),
        When(name__istartswith=raw.strip(), then=Value(80)),
        When(name__icontains=raw.strip(), then=Value(60)),
        When(category__name__icontains=raw.strip(), then=Value(40)),
        When(search_vector__icontains=normalized, then=Value(30)),
    ]
    parsed = parse_product_query(raw)
    if parsed:
        whens.insert(
            0,
            When(series_code=parsed.series_code, then=Value(90)),
        )
        if parsed.product_type:
            whens.insert(
                0,
                When(
                    series_code=parsed.series_code,
                    product_type=parsed.product_type,
                    then=Value(95),
                ),
            )
    product_type = PRODUCT_TYPE_QUERY_ALIASES.get(normalized)
    if product_type:
        whens.append(When(product_type=product_type, then=Value(20)))
    return qs.annotate(
        relevance=Case(*whens, default=Value(0), output_field=IntegerField()),
    )


def search_products_queryset(query: str) -> QuerySet[ProductGroup]:
    """Search ProductGroup by trigram similarity and catalog text match."""
    from django.db import connection

    raw = query.strip()
    if not raw:
        return ProductGroup.objects.none()

    normalized = normalize_search_query(raw)
    direct = _build_direct_match_q(raw, normalized)

    qs = (
        ProductGroup.objects.filter(is_active=True, category_id__in=get_public_category_ids())
        .select_related("category")
        .prefetch_related("variants", "images")
    )

    if connection.vendor == "postgresql" and len(normalized) >= 3:
        qs = (
            qs.annotate(
                rank=Greatest(
                    TrigramSimilarity("search_vector", normalized),
                    TrigramSimilarity("series_code", normalized),
                    Value(0.0),
                )
            )
            .filter(Q(rank__gt=0.12) | direct)
        )
        qs = _annotate_relevance(qs, raw, normalized).order_by(
            "-relevance", "-rank", "sort_order", "name",
        )
    else:
        qs = _annotate_relevance(qs.filter(direct), raw, normalized).order_by(
            "-relevance", "sort_order", "name",
        )

    return qs.distinct()


def search_products(query: str, limit: int = 24) -> QuerySet[ProductGroup]:
    return search_products_queryset(query)[:limit]


def resolve_search_to_product(query: str) -> ProductGroup | None:
    """
    Best single product for a short catalog query (кт6023, KT 6023, …).
    Returns None when ambiguous (e.g. КТ и КТП с одной серией без уточнения).
    """
    raw = query.strip()
    if len(raw) < 2:
        return None

    base = ProductGroup.objects.filter(
        is_active=True,
        category_id__in=get_public_category_ids(),
    )

    parsed = parse_product_query(raw)
    if parsed:
        qs = base.filter(series_code=parsed.series_code)
        if parsed.product_type:
            qs = qs.filter(product_type=parsed.product_type)
        if parsed.execution:
            qs = qs.filter(
                variants__execution=parsed.execution,
                variants__is_active=True,
            )
        matches = list(qs.distinct().order_by("sort_order", "name")[:6])
        if len(matches) == 1:
            return matches[0]
        if len(matches) > 1 and parsed.execution:
            return matches[0]

        from apps.products.services.catalog_parser import build_group_slug
        from apps.products.services.catalog_path_resolve import find_group_by_catalog_segment

        ptype = parsed.product_type or ProductGroup.ProductType.KT
        for execution in (parsed.execution, "B", "BS", "S", None):
            for current in (None, 160, 250, 100, 125, 80, 400, 630, 1000):
                slug = build_group_slug(
                    ptype,
                    parsed.series_code,
                    current,
                    execution if execution not in (None, "NONE") else None,
                )
                hit = find_group_by_catalog_segment(slug, base)
                if hit:
                    return hit

    results = list(search_products_queryset(raw)[:4])
    if not results:
        return None
    if len(results) == 1:
        return results[0]

    rel = [getattr(g, "relevance", 0) or 0 for g in results]
    if rel[0] >= 85 and rel[0] - rel[1] >= 25:
        return results[0]

    if parsed:
        same_series = [g for g in results if g.series_code == parsed.series_code]
        if len(same_series) == 1:
            return same_series[0]
        if parsed.product_type:
            typed = [g for g in same_series if g.product_type == parsed.product_type]
            if len(typed) == 1:
                return typed[0]

    return None
