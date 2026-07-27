import pytest
from rest_framework.test import APIClient

from apps.products.models import Category, ProductGroup, ProductVariant


@pytest.fixture
def api_client():
    return APIClient()


@pytest.mark.django_db
def test_price_from_ignores_zero_price_coil_variants(api_client):
    category = Category.objects.create(name="КТ 6000", slug="kt-6000b")
    group = ProductGroup.objects.create(
        name="Контактор КТ 6012 100А",
        slug="kontaktor-kt-6012-100a-b",
        category=category,
        product_type="KT",
        series_code="6012",
        nominal_current_a=100,
    )
    ProductVariant.objects.create(
        group=group,
        sku_code="КТ6012Б-У3",
        slug="kt6012b-u3",
        execution="B",
        coil_voltage_v=220,
        price=7320,
        is_default=True,
    )
    ProductVariant.objects.create(
        group=group,
        sku_code="КТ6012Б-У3-380V",
        slug="kt6012b-u3-380v",
        execution="B",
        coil_voltage_v=380,
        price=0,
    )

    response = api_client.get("/api/v1/products/kontaktor-kt-6012-100a-b/")
    assert response.status_code == 200
    assert float(response.data["price_from"]) == 7320.0
    assert float(response.data["default_variant"]["price"]) == 7320.0

    listing = api_client.get("/api/v1/products/").data["results"]
    match = next(item for item in listing if item["slug"] == group.slug)
    assert float(match["price_from"]) == 7320.0
