import pytest
from django.core.management import call_command
from rest_framework.test import APIClient

from apps.content.models import Page
from apps.products.models import Category, ProductGroup, ProductVariant
from apps.products.services.search import rebuild_all_search_indexes


@pytest.fixture
def api_client():
    return APIClient()


@pytest.mark.django_db
def test_search_text_query_does_not_return_unrelated_products(api_client):
    kt_cat = Category.objects.create(name="Контакторы КТ", slug="kontaktory-kt")
    ktp_cat = Category.objects.create(name="Контакторы КТП", slug="kontaktory-ktp")
    acc_cat = Category.objects.create(name="Механические блокировки", slug="meh-blokirovki")

    kt_group = ProductGroup.objects.create(
        name="Контактор КТ 6043 400А",
        slug="kontaktor-kt-6043-400a",
        category=kt_cat,
        product_type="KT",
        series_code="6043",
        nominal_current_a=400,
    )
    ProductVariant.objects.create(
        group=kt_group, sku_code="КТ6043Б-У3", slug="kt6043b-u3",
        execution="B", price=25100, is_default=True,
    )
    ProductGroup.objects.create(
        name="Контактор КТП 6012",
        slug="kontaktor-ktp-6012",
        category=ktp_cat,
        product_type="KTP",
        series_code="6012",
    )
    meh_group = ProductGroup.objects.create(
        name="Механическая блокировка МБ-1",
        slug="meh-blokirovka-mb1",
        category=acc_cat,
        product_type="ACCESSORY",
        short_description="Блокировка для контакторов серии КТ",
    )
    ProductVariant.objects.create(
        group=meh_group, sku_code="МБ-1", slug="mb-1",
        execution="NONE", price=1200, is_default=True,
    )
    rebuild_all_search_indexes()

    kt_response = api_client.get("/api/v1/search/", {"q": "КТ"})
    assert kt_response.status_code == 200
    kt_slugs = {r["slug"] for r in kt_response.data["results"]}
    assert "kontaktor-kt-6043-400a" in kt_slugs
    assert "kontaktor-ktp-6012" not in kt_slugs
    assert "meh-blokirovka-mb1" not in kt_slugs

    meh_response = api_client.get("/api/v1/search/", {"q": "мех"})
    assert meh_response.status_code == 200
    meh_slugs = {r["slug"] for r in meh_response.data["results"]}
    assert "meh-blokirovka-mb1" in meh_slugs
    assert "kontaktor-kt-6043-400a" not in meh_slugs


@pytest.mark.django_db
def test_search_finds_series(api_client):
    root = Category.objects.create(name="Контакторы КТ", slug="kontaktory-kt")
    child = Category.objects.create(name="Серия 6000", slug="kt-6000", parent=root)
    group = ProductGroup.objects.create(
        name="Контактор КТ 6043 400А",
        slug="kontaktor-kt-6043-400a",
        category=child,
        product_type="KT",
        series_code="6043",
        nominal_current_a=400,
    )
    ProductVariant.objects.create(
        group=group, sku_code="КТ6043Б-У3", slug="kt6043b-u3",
        execution="B", price=25100, is_default=True,
    )
    rebuild_all_search_indexes()

    response = api_client.get("/api/v1/search/", {"q": "кт6043"})
    assert response.status_code == 200
    assert response.data["count"] >= 1
    assert any("6043" in r["series_code"] for r in response.data["results"])


@pytest.mark.django_db
def test_search_suggest(api_client):
    root = Category.objects.create(name="Контакторы КТ", slug="kontaktory-kt")
    child = Category.objects.create(name="Серия 6000", slug="kt-6000", parent=root)
    group = ProductGroup.objects.create(
        name="Контактор КТ 6043 400А",
        slug="kontaktor-kt-6043-400a",
        category=child,
        product_type="KT",
        series_code="6043",
        nominal_current_a=400,
    )
    ProductVariant.objects.create(
        group=group, sku_code="КТ6043Б-У3", slug="kt6043b-u3",
        execution="B", price=25100, is_default=True,
    )
    rebuild_all_search_indexes()

    response = api_client.get("/api/v1/search/suggest/", {"q": "кт60"})
    assert response.status_code == 200
    assert len(response.data["suggestions"]) >= 1
    assert response.data["suggestions"][0]["sku"] == "КТ6043Б-У3"


@pytest.mark.django_db
def test_page_about_api(api_client):
    Page.objects.create(
        title="О заводе", slug="about", body="<p>Test</p>", is_published=True,
    )
    response = api_client.get("/api/v1/pages/about/")
    assert response.status_code == 200
    assert response.data["slug"] == "about"
    assert "Test" in response.data["body"]
