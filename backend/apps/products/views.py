from django.conf import settings
from django.core.cache import cache
from django.db.models import Min, Prefetch, Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, status
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response
from rest_framework.views import APIView

from config.pagination import CatalogPagination

from apps.seo.models import SearchQueryLog

from .filters import ProductGroupFilter
from .models import Category, ProductGroup, ProductSpec, ProductVariant
from .serializers import (
    CategoryTreeSerializer,
    CompareVariantSerializer,
    ProductGroupDetailSerializer,
    ProductGroupListSerializer,
    ProductVariantDetailSerializer,
)
from .services.catalog_filter import (
    apply_catalog_filters,
    base_product_queryset,
    build_filters_meta,
    order_queryset,
    params_from_request,
    params_to_dict,
)
from .services.search import search_products, search_products_queryset
from .utils import CATEGORIES_CACHE_KEY, get_public_category_ids

CATEGORIES_CACHE_TTL = getattr(settings, "CACHE_TTL_CATEGORIES", 3600)


def get_product_queryset():
    return (
        ProductGroup.objects.filter(is_active=True, category_id__in=get_public_category_ids())
        .select_related("category")
        .prefetch_related(
            Prefetch("variants", queryset=ProductVariant.objects.filter(is_active=True)),
            "images",
        )
        .annotate(min_price=Min("variants__price", filter=Q(variants__is_active=True)))
    )


class CategoryListView(APIView):
    """GET /api/v1/categories/ — MPTT tree, cached in production."""

    def get(self, request):
        if not settings.DEBUG:
            cached = cache.get(CATEGORIES_CACHE_KEY)
            if cached is not None:
                return Response(cached)

        roots = (
            Category.objects.filter(is_active=True, parent__isnull=True)
            .order_by("sort_order", "name")
        )
        data = CategoryTreeSerializer(roots, many=True, context={"request": request}).data

        if not settings.DEBUG:
            cache.set(CATEGORIES_CACHE_KEY, data, CATEGORIES_CACHE_TTL)

        response = Response(data)
        response["Cache-Control"] = "no-store, max-age=0" if settings.DEBUG else "public, max-age=300"
        return response


class ProductGroupListView(generics.ListAPIView):
    """GET /api/v1/products/ — list with faceted filters."""

    serializer_class = ProductGroupListSerializer
    pagination_class = CatalogPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ProductGroupFilter
    search_fields = ["name", "series_code", "variants__sku_code"]
    ordering_fields = ["name", "nominal_current_a", "min_price"]
    ordering = ["sort_order", "name"]

    def get_queryset(self):
        return get_product_queryset()


class ProductGroupDetailView(generics.RetrieveAPIView):
    """GET /api/v1/products/{slug}/"""

    serializer_class = ProductGroupDetailSerializer
    lookup_field = "slug"

    def get_queryset(self):
        return (
            ProductGroup.objects.filter(is_active=True, category_id__in=get_public_category_ids())
            .select_related("category")
            .prefetch_related(
                Prefetch("variants", queryset=ProductVariant.objects.filter(is_active=True)),
                "specs", "images",
                "documents__document",
                "related_groups",
            )
            .annotate(min_price=Min("variants__price", filter=Q(variants__is_active=True)))
        )


class ProductVariantDetailView(generics.RetrieveAPIView):
    """GET /api/v1/variants/{slug}/"""

    serializer_class = ProductVariantDetailSerializer
    lookup_field = "slug"

    def get_queryset(self):
        return (
            ProductVariant.objects.filter(
                is_active=True,
                group__is_active=True,
                group__category_id__in=get_public_category_ids(),
            )
            .select_related("group", "group__category")
            .prefetch_related("group__specs")
        )


class CompareView(APIView):
    """GET /api/v1/compare/?ids=1,2,3,4 — max 4 variants."""

    MAX_ITEMS = 4

    def get(self, request):
        ids_param = request.query_params.get("ids", "")
        if not ids_param:
            return Response({"detail": "Parameter ids is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            ids = [int(x.strip()) for x in ids_param.split(",") if x.strip()]
        except ValueError:
            return Response({"detail": "ids must be comma-separated integers"}, status=status.HTTP_400_BAD_REQUEST)

        if not ids or len(ids) > self.MAX_ITEMS:
            return Response(
                {"detail": f"Provide 1 to {self.MAX_ITEMS} variant ids"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        variants = (
            ProductVariant.objects.filter(
                id__in=ids,
                is_active=True,
                group__is_active=True,
                group__category_id__in=get_public_category_ids(),
            )
            .select_related("group")
            .prefetch_related("group__specs")
        )
        if variants.count() != len(set(ids)):
            return Response({"detail": "One or more variants not found"}, status=status.HTTP_404_NOT_FOUND)

        id_order = {vid: idx for idx, vid in enumerate(ids)}
        sorted_variants = sorted(variants, key=lambda v: id_order.get(v.id, 999))

        spec_keys = list(
            ProductSpec.objects.filter(group__in=[v.group for v in sorted_variants], filterable=True)
            .values_list("spec_key", flat=True)
            .distinct()
            .order_by("spec_key")
        )

        return Response({
            "variants": CompareVariantSerializer(
                sorted_variants, many=True, context={"request": request},
            ).data,
            "spec_keys": spec_keys,
        })


class SearchView(APIView):
    """GET /api/v1/search/?q= — trigram search with pagination (STEP-035, 057)."""

    @staticmethod
    def _client_ip(request) -> str | None:
        forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR")

    def get(self, request):
        q = request.query_params.get("q", "").strip()
        if not q:
            return Response({"detail": "Parameter q is required"}, status=status.HTTP_400_BAD_REQUEST)

        qs = search_products_queryset(q).annotate(
            min_price=Min("variants__price", filter=Q(variants__is_active=True)),
        )
        filterset = ProductGroupFilter(request.GET, queryset=qs)
        qs = filterset.qs

        ordering = request.query_params.get("ordering", "").strip()
        allowed_ordering = {
            "name", "-name", "nominal_current_a", "-nominal_current_a",
            "min_price", "-min_price", "sort_order", "-sort_order",
        }
        if ordering in allowed_ordering:
            qs = qs.order_by(ordering)

        total_count = qs.count()
        if total_count == 0:
            SearchQueryLog.objects.create(
                query=q[:255],
                results_count=0,
                ip=self._client_ip(request),
            )

        paginator = CatalogPagination()
        page = paginator.paginate_queryset(qs, request, view=self)
        data = ProductGroupListSerializer(page, many=True, context={"request": request}).data
        response = paginator.get_paginated_response(data)
        response.data["query"] = q
        return response


class SearchSuggestView(APIView):
    """GET /api/v1/search/suggest/?q= — cached autocomplete (STEP-056)."""

    CACHE_TTL = getattr(settings, "CACHE_TTL_SEARCH_SUGGEST", 300)
    MIN_QUERY_LEN = 2
    MAX_SUGGESTIONS = 8

    def get(self, request):
        q = request.query_params.get("q", "").strip()
        if len(q) < self.MIN_QUERY_LEN:
            return Response({"query": q, "suggestions": []})

        cache_key = f"search:suggest:{q.lower()[:80]}"
        cached = cache.get(cache_key)
        if cached is not None:
            return Response(cached)

        groups = search_products(q, limit=self.MAX_SUGGESTIONS)
        suggestions = []
        for group in groups:
            variant = (
                group.variants.filter(is_active=True, is_default=True).first()
                or group.variants.filter(is_active=True).order_by("price").first()
            )
            suggestions.append({
                "name": group.name,
                "sku": variant.sku_code if variant else group.series_code,
                "category_name": group.category.name,
                "category_slug": group.category.slug,
                "product_slug": group.slug,
                "variant_id": variant.id if variant else None,
            })

        payload = {"query": q, "suggestions": suggestions}
        cache.set(cache_key, payload, self.CACHE_TTL)
        return Response(payload)


class CatalogFilterView(APIView):
    """GET /api/v1/catalog/filter/ — smart filter with facets and pagination."""

    CACHE_TTL = getattr(settings, "CACHE_TTL_CATALOG_FILTER", 300)

    def get(self, request):
        params = params_from_request(request.query_params)
        cache_key = f"catalog:filter:{hash(frozenset(request.query_params.items()))}"
        if not settings.DEBUG:
            cached = cache.get(cache_key)
            if cached is not None:
                return Response(cached)

        qs = base_product_queryset()
        filtered = apply_catalog_filters(qs, params)
        filtered = order_queryset(filtered, params.ordering)

        total = filtered.count()
        start = (params.page - 1) * params.page_size
        page_qs = filtered[start : start + params.page_size]

        page_qs = (
            page_qs.select_related("category")
            .prefetch_related(
                Prefetch("variants", queryset=ProductVariant.objects.filter(is_active=True)),
                "images",
            )
            .annotate(min_price=Min("variants__price", filter=Q(variants__is_active=True)))
        )

        products = ProductGroupListSerializer(
            page_qs, many=True, context={"request": request},
        ).data
        filters_meta = build_filters_meta(qs, params)

        payload = {
            "status": "success",
            "count": total,
            "results": products,
            "current_page": params.page,
            "last_page": max(1, (total + params.page_size - 1) // params.page_size),
            "filters_meta": filters_meta,
            "applied_filters": params_to_dict(params),
        }

        if not settings.DEBUG:
            cache.set(cache_key, payload, self.CACHE_TTL)

        response = Response(payload)
        response["Cache-Control"] = "no-store, max-age=0" if settings.DEBUG else "public, max-age=300"
        return response
