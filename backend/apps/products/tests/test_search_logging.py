import pytest
from rest_framework.test import APIClient

from apps.products.models import Category, ProductGroup
from apps.seo.models import SearchQueryLog


@pytest.fixture
def api_client():
    return APIClient()


@pytest.mark.django_db
def test_search_logs_zero_results(api_client):
    response = api_client.get("/api/v1/search/", {"q": "nonexistent-sku-xyz-999"})
    assert response.status_code == 200
    assert response.data["count"] == 0
    assert SearchQueryLog.objects.filter(query="nonexistent-sku-xyz-999").exists()


@pytest.mark.django_db
def test_search_does_not_log_when_results_found(api_client):
    cat = Category.objects.create(name="КТ", slug="kt")
    ProductGroup.objects.create(name="Контактор", slug="kontaktor", category=cat, series_code="KT1")
    response = api_client.get("/api/v1/search/", {"q": "Контактор"})
    assert response.status_code == 200
    assert response.data["count"] >= 1
    assert not SearchQueryLog.objects.filter(query="Контактор").exists()
