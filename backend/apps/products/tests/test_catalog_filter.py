import pytest
from rest_framework.test import APIClient

from apps.products.models import Category, ProductGroup, ProductVariant


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def catalog_tree(db):
    root_kt = Category.objects.create(name="Контакторы КТ", slug="kontaktory-kt", sort_order=1)
    root_switch = Category.objects.create(name="Выключатели", slug="vyklyuchateli", sort_order=5)
    child = Category.objects.create(name="Серия 6000", slug="kt-6000", parent=root_kt)
    child_switch = Category.objects.create(name="Путевые", slug="vyklyuchateli-putevye", parent=root_switch)

    g1 = ProductGroup.objects.create(
        name="Контактор КТ 6043 400А",
        slug="kontaktor-kt-6043",
        category=child,
        product_type="KT",
        series_code="6043",
        nominal_current_a=400,
        poles=3,
        application_category="AC3",
    )
    g2 = ProductGroup.objects.create(
        name="Контактор КТ 6053 630А",
        slug="kontaktor-kt-6053",
        category=child,
        product_type="KT",
        series_code="6053",
        nominal_current_a=630,
        poles=3,
    )
    g3 = ProductGroup.objects.create(
        name="Выключатель ВПК",
        slug="vyklyuchatel-vpk",
        category=child_switch,
        product_type="SWITCH",
        nominal_current_a=100,
    )
    ProductVariant.objects.create(
        group=g1, sku_code="KT6043B-U3", slug="kt6043b-u3",
        execution="B", coil_voltage_v=380, price=25100, is_default=True,
    )
    ProductVariant.objects.create(
        group=g2, sku_code="KT6053B-U3", slug="kt6053b-u3",
        execution="B", coil_voltage_v=380, price=32675, is_default=True,
    )
    return {"g1": g1, "g2": g2, "g3": g3}


@pytest.mark.django_db
def test_catalog_filter_returns_products_and_meta(api_client, catalog_tree):
    response = api_client.get("/api/v1/catalog/filter/", {"category": "kt-6000"})
    assert response.status_code == 200
    assert response.data["status"] == "success"
    assert response.data["count"] == 2
    slugs = [p["slug"] for p in response.data["results"]]
    assert "kontaktor-kt-6043" in slugs
    assert "vyklyuchatel-vpk" not in slugs
    assert "filters_meta" in response.data
    assert "current_rating" in response.data["filters_meta"]


@pytest.mark.django_db
def test_catalog_filter_current_range(api_client, catalog_tree):
    response = api_client.get(
        "/api/v1/catalog/filter/",
        {"category": "kontaktory-kt", "current_min": 400, "current_max": 500},
    )
    assert response.status_code == 200
    assert response.data["count"] == 1
    assert response.data["results"][0]["slug"] == "kontaktor-kt-6043"


@pytest.mark.django_db
def test_catalog_filter_type_facets_update(api_client, catalog_tree):
    response = api_client.get(
        "/api/v1/catalog/filter/",
        {"type": "kontaktory-kt"},
    )
    assert response.status_code == 200
    assert response.data["count"] == 2
    meta = response.data["filters_meta"]
    assert meta["category_type"]["kontaktory-kt"]["count"] == 2
    assert meta["category_type"].get("vyklyuchateli", {}).get("count", 0) == 0 or "vyklyuchateli" not in meta["category_type"] or meta["category_type"]["vyklyuchateli"]["count"] == 1
