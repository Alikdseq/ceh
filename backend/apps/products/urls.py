from django.urls import path

from .views import (
    CatalogFilterView,
    CategoryListView,
    CompareView,
    ProductGroupDetailView,
    ProductGroupListView,
    ProductVariantDetailView,
    SearchSuggestView,
    SearchView,
)

urlpatterns = [
    path("categories/", CategoryListView.as_view(), name="category-list"),
    path("catalog/filter/", CatalogFilterView.as_view(), name="catalog-filter"),
    path("products/", ProductGroupListView.as_view(), name="product-list"),
    path("products/<slug:slug>/", ProductGroupDetailView.as_view(), name="product-detail"),
    path("variants/<slug:slug>/", ProductVariantDetailView.as_view(), name="variant-detail"),
    path("compare/", CompareView.as_view(), name="compare"),
    path("search/suggest/", SearchSuggestView.as_view(), name="search-suggest"),
    path("search/", SearchView.as_view(), name="search"),
]
