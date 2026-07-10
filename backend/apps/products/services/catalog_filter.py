"""Smart catalog filter: apply filters (AND) + facet counts (deep filtering)."""
from __future__ import annotations

from dataclasses import dataclass, field

from django.db.models import Count, Max, Min, Q, QuerySet

from apps.docs.models import Document
from apps.products.models import Category, ProductGroup, ProductVariant
from apps.products.utils import get_public_category_ids


DOC_TYPE_MAP = {
    "passport": [Document.DocType.PASSPORT, Document.DocType.TU],
    "certificate": [Document.DocType.CERTIFICATE],
    "drawing": [Document.DocType.DRAWING_DWG, Document.DocType.DRAWING_PDF],
}


@dataclass
class CatalogFilterParams:
    category: str | None = None
    type_slugs: list[str] = field(default_factory=list)
    product_types: list[str] = field(default_factory=list)
    current_min: int | None = None
    current_max: int | None = None
    current_values: list[int] = field(default_factory=list)
    coil_min: int | None = None
    coil_max: int | None = None
    coil_values: list[int] = field(default_factory=list)
    executions: list[str] = field(default_factory=list)
    poles_values: list[int] = field(default_factory=list)
    series_codes: list[str] = field(default_factory=list)
    climates: list[str] = field(default_factory=list)
    applications: list[str] = field(default_factory=list)
    documents: list[str] = field(default_factory=list)
    featured: bool | None = None
    ordering: str | None = None
    page: int = 1
    page_size: int = 24


def parse_int(value: str | None) -> int | None:
    if value is None or value == "":
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def parse_list(values: list[str] | None, single: str | None = None) -> list[str]:
    result: list[str] = []
    if values:
        for item in values:
            result.extend(x.strip() for x in item.split(",") if x.strip())
    if single:
        result.extend(x.strip() for x in single.split(",") if x.strip())
    seen: set[str] = set()
    unique: list[str] = []
    for item in result:
        if item not in seen:
            seen.add(item)
            unique.append(item)
    return unique


def parse_int_list(values: list[str] | None, single: str | None = None) -> list[int]:
    parsed: list[int] = []
    for raw in parse_list(values, single):
        num = parse_int(raw)
        if num is not None:
            parsed.append(num)
    return parsed


def params_from_request(query_params) -> CatalogFilterParams:
    return CatalogFilterParams(
        category=(query_params.get("category") or "").strip() or None,
        type_slugs=parse_list(query_params.getlist("type"), query_params.get("type")),
        product_types=parse_list(
            query_params.getlist("product_type"),
            query_params.get("product_type"),
        ),
        current_min=parse_int(query_params.get("current_min")),
        current_max=parse_int(query_params.get("current_max")),
        current_values=parse_int_list(
            query_params.getlist("current"),
            query_params.get("current"),
        ),
        coil_min=parse_int(query_params.get("coil_min")),
        coil_max=parse_int(query_params.get("coil_max")),
        coil_values=parse_int_list(
            query_params.getlist("coil"),
            query_params.get("coil"),
        ),
        executions=parse_list(
            query_params.getlist("execution"),
            query_params.get("execution"),
        ),
        poles_values=parse_int_list(
            query_params.getlist("poles"),
            query_params.get("poles"),
        ),
        series_codes=parse_list(
            query_params.getlist("series"),
            query_params.get("series"),
        ),
        climates=parse_list(
            query_params.getlist("climate"),
            query_params.get("climate"),
        ),
        applications=parse_list(
            query_params.getlist("application"),
            query_params.get("application"),
        ),
        documents=parse_list(query_params.getlist("doc"), query_params.get("doc")),
        featured=(
            True
            if query_params.get("featured", "").lower() in ("1", "true", "yes")
            else None
        ),
        ordering=(query_params.get("ordering") or "").strip() or None,
        page=max(1, parse_int(query_params.get("page")) or 1),
        page_size=min(48, max(1, parse_int(query_params.get("page_size")) or 24)),
    )


def params_to_dict(params: CatalogFilterParams) -> dict:
    return {
        "category": params.category,
        "type": params.type_slugs,
        "product_type": params.product_types,
        "current_min": params.current_min,
        "current_max": params.current_max,
        "current": params.current_values,
        "coil_min": params.coil_min,
        "coil_max": params.coil_max,
        "coil": params.coil_values,
        "execution": params.executions,
        "poles": params.poles_values,
        "series": params.series_codes,
        "climate": params.climates,
        "application": params.applications,
        "doc": params.documents,
        "featured": params.featured,
        "ordering": params.ordering,
        "page": params.page,
        "page_size": params.page_size,
    }


def _category_ids_for_slug(slug: str) -> list[int]:
    cat = Category.objects.filter(slug=slug, is_active=True).first()
    if not cat:
        return []
    return list(
        cat.get_descendants(include_self=True)
        .filter(is_active=True)
        .values_list("id", flat=True)
    )


def _category_ids_for_root_slugs(slugs: list[str]) -> list[int]:
    if not slugs:
        return []
    ids: set[int] = set()
    for root in Category.objects.filter(slug__in=slugs, parent__isnull=True, is_active=True):
        ids.update(
            root.get_descendants(include_self=True)
            .filter(is_active=True)
            .values_list("id", flat=True)
        )
    return list(ids)


def apply_catalog_filters(
    qs: QuerySet[ProductGroup],
    params: CatalogFilterParams,
    *,
    exclude: frozenset[str] | None = None,
) -> QuerySet[ProductGroup]:
    exclude = exclude or frozenset()

    if "category" not in exclude and params.category:
        cat_ids = _category_ids_for_slug(params.category)
        qs = qs.filter(category_id__in=cat_ids) if cat_ids else qs.none()

    if "type" not in exclude and params.type_slugs:
        cat_ids = _category_ids_for_root_slugs(params.type_slugs)
        qs = qs.filter(category_id__in=cat_ids) if cat_ids else qs.none()

    if "product_type" not in exclude and params.product_types:
        qs = qs.filter(product_type__in=params.product_types)

    if "current" not in exclude:
        if params.current_values:
            qs = qs.filter(nominal_current_a__in=params.current_values)
        else:
            if params.current_min is not None:
                qs = qs.filter(nominal_current_a__gte=params.current_min)
            if params.current_max is not None:
                qs = qs.filter(nominal_current_a__lte=params.current_max)

    if "coil" not in exclude:
        coil_q = Q()
        if params.coil_values:
            coil_q |= Q(variants__coil_voltage_v__in=params.coil_values, variants__is_active=True)
        else:
            if params.coil_min is not None:
                coil_q |= Q(variants__coil_voltage_v__gte=params.coil_min, variants__is_active=True)
            if params.coil_max is not None:
                coil_q |= Q(variants__coil_voltage_v__lte=params.coil_max, variants__is_active=True)
        if coil_q:
            qs = qs.filter(coil_q).distinct()

    if "execution" not in exclude and params.executions:
        qs = qs.filter(
            variants__execution__in=params.executions,
            variants__is_active=True,
        ).distinct()

    if "poles" not in exclude and params.poles_values:
        qs = qs.filter(poles__in=params.poles_values)

    if "series" not in exclude and params.series_codes:
        qs = qs.filter(series_code__in=params.series_codes)

    if "climate" not in exclude and params.climates:
        qs = qs.filter(application_category__in=params.climates)

    if "application" not in exclude and params.applications:
        qs = qs.filter(application_category__in=params.applications)

    if "doc" not in exclude and params.documents:
        doc_types: list[str] = []
        for key in params.documents:
            doc_types.extend(DOC_TYPE_MAP.get(key, []))
        if doc_types:
            qs = qs.filter(
                documents__document__doc_type__in=doc_types,
                documents__document__is_public=True,
            ).distinct()

    if "featured" not in exclude and params.featured:
        qs = qs.filter(is_featured=True)

    return qs


def base_product_queryset() -> QuerySet[ProductGroup]:
    return ProductGroup.objects.filter(
        is_active=True,
        category_id__in=get_public_category_ids(),
    )


def order_queryset(qs: QuerySet[ProductGroup], ordering: str | None) -> QuerySet[ProductGroup]:
    allowed = {
        "name", "-name", "nominal_current_a", "-nominal_current_a",
        "min_price", "-min_price", "sort_order", "-sort_order",
    }
    if ordering in allowed:
        return qs.order_by(ordering)
    return qs.order_by("sort_order", "name")


def _count_map(qs: QuerySet[ProductGroup], field: str) -> dict[str, int]:
    filtered = qs.exclude(**{f"{field}__isnull": True})
    if qs.model._meta.get_field(field).get_internal_type() in ("CharField", "TextField", "SlugField"):
        filtered = filtered.exclude(**{field: ""})
    rows = (
        filtered.values(field)
        .annotate(count=Count("id", distinct=True))
        .order_by(field)
    )
    return {str(row[field]): row["count"] for row in rows}


def _variant_count_map(qs: QuerySet[ProductGroup], field: str) -> dict[str, int]:
    rows = (
        ProductVariant.objects.filter(
            is_active=True,
            group__in=qs,
        )
        .exclude(**{f"{field}__isnull": True})
        .values(field)
        .annotate(count=Count("group_id", distinct=True))
        .order_by(field)
    )
    return {str(row[field]): row["count"] for row in rows}


def build_filters_meta(
    qs: QuerySet[ProductGroup],
    params: CatalogFilterParams,
) -> dict:
    meta: dict = {}

    type_qs = apply_catalog_filters(qs, params, exclude=frozenset({"type"}))
    type_counts: dict[str, dict] = {}
    for root in Category.objects.filter(parent__isnull=True, is_active=True).order_by("sort_order", "name"):
        cat_ids = list(
            root.get_descendants(include_self=True)
            .filter(is_active=True)
            .values_list("id", flat=True)
        )
        count = type_qs.filter(category_id__in=cat_ids).count()
        if count:
            type_counts[root.slug] = {"name": root.name, "count": count}
    meta["category_type"] = type_counts

    pt_qs = apply_catalog_filters(qs, params, exclude=frozenset({"product_type"}))
    meta["product_type"] = _count_map(pt_qs, "product_type")

    cur_qs = apply_catalog_filters(qs, params, exclude=frozenset({"current"}))
    cur_agg = cur_qs.aggregate(
        min=Min("nominal_current_a"),
        max=Max("nominal_current_a"),
    )
    available_current = sorted(
        {
            v
            for v in cur_qs.exclude(nominal_current_a__isnull=True).values_list(
                "nominal_current_a", flat=True,
            )
            if v is not None
        }
    )
    meta["current_rating"] = {
        "min": cur_agg["min"],
        "max": cur_agg["max"],
        "available": available_current,
        "counts": _count_map(cur_qs, "nominal_current_a"),
    }

    coil_qs = apply_catalog_filters(qs, params, exclude=frozenset({"coil"}))
    coil_values = sorted(
        {
            v
            for v in ProductVariant.objects.filter(
                is_active=True,
                group__in=coil_qs,
            )
            .exclude(coil_voltage_v__isnull=True)
            .values_list("coil_voltage_v", flat=True)
            if v is not None
        }
    )
    coil_agg = ProductVariant.objects.filter(
        is_active=True,
        group__in=coil_qs,
    ).aggregate(min=Min("coil_voltage_v"), max=Max("coil_voltage_v"))
    meta["coil_voltage"] = {
        "min": coil_agg["min"],
        "max": coil_agg["max"],
        "available": coil_values,
        "counts": _variant_count_map(coil_qs, "coil_voltage_v"),
    }

    exec_qs = apply_catalog_filters(qs, params, exclude=frozenset({"execution"}))
    meta["execution"] = _variant_count_map(exec_qs, "execution")

    poles_qs = apply_catalog_filters(qs, params, exclude=frozenset({"poles"}))
    meta["poles"] = _count_map(poles_qs, "poles")

    series_qs = apply_catalog_filters(qs, params, exclude=frozenset({"series"}))
    meta["series"] = _count_map(series_qs, "series_code")

    app_qs = apply_catalog_filters(qs, params, exclude=frozenset({"climate", "application"}))
    meta["application"] = _count_map(app_qs, "application_category")

    doc_qs = apply_catalog_filters(qs, params, exclude=frozenset({"doc"}))
    doc_counts: dict[str, int] = {}
    for key, doc_types in DOC_TYPE_MAP.items():
        doc_counts[key] = (
            doc_qs.filter(
                documents__document__doc_type__in=doc_types,
                documents__document__is_public=True,
            )
            .distinct()
            .count()
        )
    meta["documentation"] = doc_counts

    return meta
