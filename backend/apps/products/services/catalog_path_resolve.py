"""Resolve product catalog URLs and legacy slug aliases (6612/6622, old paths)."""

from __future__ import annotations

import re

from django.db.models import Q, QuerySet

from apps.products.models import ProductGroup, ProductVariant
from apps.products.services.catalog_parser import build_group_slug
from apps.products.utils import get_public_category_ids, product_catalog_path

CATALOG_SEGMENT_RE = re.compile(
    r"^kontaktor-(?P<ptype>kt|ktp|kte)-(?P<series>\d{4})(?:-(?P<current>\d+)a)?(?:-(?P<exec>b|bs|s))?$",
    re.IGNORECASE,
)


def _public_groups() -> QuerySet[ProductGroup]:
    return ProductGroup.objects.filter(is_active=True, category_id__in=get_public_category_ids())


def _execution_from_suffix(suffix: str | None) -> str | None:
    if not suffix:
        return None
    return {"b": "B", "bs": "BS", "s": "S"}.get(suffix.lower())


def _series_codes_in_name(name: str) -> list[str]:
    return list(dict.fromkeys(re.findall(r"\d{4}", name or "")))


def alternate_group_slugs(group: ProductGroup) -> set[str]:
    """Slug variants that should resolve to the same product card."""
    slugs: set[str] = {group.slug}
    ptype = group.product_type
    current = group.nominal_current_a
    executions = list(
        group.variants.filter(is_active=True)
        .exclude(execution="NONE")
        .values_list("execution", flat=True)
        .distinct()
    )
    if not executions:
        executions = ["NONE"]

    series_codes = {group.series_code} if group.series_code else set()
    series_codes.update(_series_codes_in_name(group.name))

    for series in series_codes:
        if not series:
            continue
        for execution in executions:
            slugs.add(build_group_slug(ptype, series, current, execution if execution != "NONE" else None))

    return {s for s in slugs if s}


def find_group_by_catalog_segment(segment: str, queryset: QuerySet[ProductGroup] | None = None) -> ProductGroup | None:
    """Find product by URL slug or legacy alias (e.g. 6622 → card for 6612/6622)."""
    if not segment:
        return None
    segment = segment.strip().lower()
    qs = queryset if queryset is not None else _public_groups()

    hit = qs.filter(slug=segment).first()
    if hit:
        return hit

    match = CATALOG_SEGMENT_RE.match(segment)
    if match:
        ptype = match.group("ptype").upper()
        series = match.group("series")
        current = int(match.group("current")) if match.group("current") else None
        execution = _execution_from_suffix(match.group("exec"))

        built = build_group_slug(ptype, series, current, execution)
        hit = qs.filter(slug=built).first()
        if hit:
            return hit

        scoped = qs.filter(product_type=ptype)
        if current is not None:
            scoped = scoped.filter(nominal_current_a=current)
        if execution:
            scoped = scoped.filter(
                variants__execution=execution,
                variants__is_active=True,
            ).distinct()

        hit = scoped.filter(
            Q(series_code=series)
            | Q(name__icontains=series)
            | Q(variants__sku_code__icontains=series)
        ).first()
        if hit:
            return hit

    compact = segment.replace("-", "")
    if re.fullmatch(r"(kt|ktp|kte)?\d{4}[bss]*", compact, re.I):
        m = re.search(r"(\d{4})", compact)
        if m:
            series = m.group(1)
            ptype = "KTP" if compact.startswith("ktp") else "KT" if compact.startswith("kt") else None
            scoped = qs.filter(Q(series_code=series) | Q(name__icontains=series))
            if ptype:
                scoped = scoped.filter(product_type=ptype)
            hit = scoped.first()
            if hit:
                return hit

    return None


def collect_catalog_redirects() -> list[tuple[str, str]]:
    """(old_path, new_path) pairs for legacy catalog URLs."""
    pairs: list[tuple[str, str]] = []
    seen: set[str] = set()

    for group in _public_groups().select_related("category").prefetch_related("variants"):
        canonical = product_catalog_path(group).rstrip("/") + "/"
        cat = group.category
        ancestors = list(cat.get_ancestors(include_self=True)) if cat else []
        leaf = cat.slug if cat else ""
        parent_path = "/".join(a.slug for a in ancestors)

        for alt in alternate_group_slugs(group):
            candidates = [
                f"/catalog/{parent_path}/{alt}/",
                f"/catalog/{leaf}/{alt}/",
            ]
            if parent_path:
                parts = parent_path.split("/")
                if len(parts) >= 2:
                    candidates.append(f"/catalog/{parts[0]}/{parts[-1]}/{alt}/")

            for old in candidates:
                if old == canonical or old in seen:
                    continue
                seen.add(old)
                pairs.append((old, canonical))

    return pairs
