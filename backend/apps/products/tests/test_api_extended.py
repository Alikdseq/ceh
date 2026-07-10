import pytest
from django.core.cache import cache
from rest_framework.test import APIClient

from apps.products.models import Category, ProductGroup, ProductVariant


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def catalog(db):
    cat = Category.objects.create(name="КТ", slug="kt")
    group = ProductGroup.objects.create(name="G", slug="g", category=cat, product_type="KT", nominal_current_a=400)
    ProductVariant.objects.create(group=group, sku_code="S1", slug="s1", execution="B", price=100, is_default=True)
    return group


@pytest.mark.django_db
def test_categories_cached(api_client, catalog):
    cache.clear()
    r1 = api_client.get("/api/v1/categories/")
    r2 = api_client.get("/api/v1/categories/")
    assert r1.status_code == 200
    assert r2.status_code == 200
    assert cache.get("api:categories:tree") is not None


@pytest.mark.django_db
def test_products_list_pagination(api_client, catalog):
    response = api_client.get("/api/v1/products/")
    assert response.status_code == 200
    assert "results" in response.data
    assert "count" in response.data


@pytest.mark.django_db
def test_products_ordering(api_client, catalog):
    response = api_client.get("/api/v1/products/", {"ordering": "name"})
    assert response.status_code == 200


@pytest.mark.django_db
def test_search_empty_query(api_client):
    response = api_client.get("/api/v1/search/", {"q": ""})
    assert response.status_code == 400


@pytest.mark.django_db
def test_search_suggest_short_query(api_client):
    response = api_client.get("/api/v1/search/suggest/", {"q": "a"})
    assert response.status_code == 200
    assert response.data["suggestions"] == []


@pytest.mark.django_db
def test_compare_requires_ids(api_client):
    response = api_client.get("/api/v1/compare/")
    assert response.status_code == 400
