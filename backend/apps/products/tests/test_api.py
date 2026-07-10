import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from apps.products.models import Category, ProductGroup, ProductSpec, ProductVariant


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def catalog_sample(db):
    root = Category.objects.create(name="Контакторы КТ", slug="kontaktory-kt")
    child = Category.objects.create(name="Серия 6000", slug="kt-6000", parent=root)
    group_b = ProductGroup.objects.create(
        name="Контактор КТ 6043 400А",
        slug="kontaktor-kt-6043",
        category=child,
        product_type="KT",
        nominal_current_a=400,
        poles=3,
    )
    group_bs = ProductGroup.objects.create(
        name="Контактор КТ 6053 630А",
        slug="kontaktor-kt-6053",
        category=child,
        product_type="KT",
        nominal_current_a=630,
        poles=3,
    )
    v1 = ProductVariant.objects.create(
        group=group_b, sku_code="KT6043B-U3", slug="kt6043b-u3",
        execution="B", coil_voltage_v=220, price=25100, is_default=True,
    )
    v2 = ProductVariant.objects.create(
        group=group_b, sku_code="KT6043B-U3-380", slug="kt6043b-u3-380",
        execution="B", coil_voltage_v=380, price=25100,
    )
    v3 = ProductVariant.objects.create(
        group=group_bs, sku_code="KT6053B-U3", slug="kt6053b-u3",
        execution="B", coil_voltage_v=380, price=32675, is_default=True,
    )
    ProductSpec.objects.create(
        group=group_b, spec_key="nominal_current", spec_value="400",
        spec_unit="А", filterable=True,
    )
    return {"root": root, "group_b": group_b, "variants": [v1, v2, v3]}


@pytest.mark.django_db
def test_inactive_category_hidden_from_api(api_client, db):
    hidden = Category.objects.create(name="Выключатели", slug="vyklyuchateli", is_active=False)
    ProductGroup.objects.create(
        name="Выключатель ВА",
        slug="vypuskatel-va",
        category=hidden,
        product_type="SWITCH",
    )
    categories = api_client.get("/api/v1/categories/").data
    assert not any(c["slug"] == "vyklyuchateli" for c in categories)
    products = api_client.get("/api/v1/products/").data
    assert "vypuskatel-va" not in [p["slug"] for p in products["results"]]
    assert api_client.get("/api/v1/products/vypuskatel-va/").status_code == 404


@pytest.mark.django_db
def test_categories_list(api_client, catalog_sample):
    response = api_client.get("/api/v1/categories/")
    assert response.status_code == 200
    assert len(response.data) >= 1
    assert response.data[0]["slug"] == "kontaktory-kt"
    assert "children" in response.data[0]


@pytest.mark.django_db
def test_products_filter_by_current(api_client, catalog_sample):
    response = api_client.get("/api/v1/products/", {"current": 400, "execution": "B"})
    assert response.status_code == 200
    slugs = [r["slug"] for r in response.data["results"]]
    assert "kontaktor-kt-6043" in slugs
    assert "kontaktor-kt-6053" not in slugs


@pytest.mark.django_db
def test_product_detail(api_client, catalog_sample):
    response = api_client.get("/api/v1/products/kontaktor-kt-6043/")
    assert response.status_code == 200
    assert len(response.data["variants"]) == 2
    assert response.data["price_from"] is not None


@pytest.mark.django_db
def test_variant_detail(api_client, catalog_sample):
    response = api_client.get("/api/v1/variants/kt6043b-u3/")
    assert response.status_code == 200
    assert response.data["sku_code"] == "KT6043B-U3"


@pytest.mark.django_db
def test_compare_max_four(api_client, catalog_sample):
    ids = ",".join(str(v.id) for v in catalog_sample["variants"])
    response = api_client.get("/api/v1/compare/", {"ids": ids})
    assert response.status_code == 200
    assert len(response.data["variants"]) == 3
    assert "spec_keys" in response.data
