import pytest
from django.utils import timezone
from rest_framework.test import APIClient

from apps.products.models import Category, ProductGroup, ProductVariant
from apps.quotes.models import QuoteCart, QuoteRequest


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def variant(db):
    cat = Category.objects.create(name="КТ", slug="kt")
    group = ProductGroup.objects.create(
        name="Контактор КТ 6043",
        slug="kontaktor-kt-6043",
        category=cat,
        product_type="KT",
        series_code="6043",
        nominal_current_a=400,
    )
    return ProductVariant.objects.create(
        group=group,
        sku_code="КТ6043Б-У3",
        slug="kt6043b-u3",
        execution="B",
        price=25100,
        coil_voltage_v=220,
        is_default=True,
    )


@pytest.mark.django_db
def test_cart_add_and_list(api_client, variant):
    response = api_client.post(
        "/api/v1/cart/items/",
        {"variant_id": variant.pk, "quantity": 2},
        format="json",
    )
    assert response.status_code == 201
    session = response["X-Cart-Session"]
    assert response.data["item_count"] == 2
    assert response.data["subtotal"] == "50200.00"

    list_resp = api_client.get("/api/v1/cart/", HTTP_X_CART_SESSION=session)
    assert list_resp.status_code == 200
    assert len(list_resp.data["items"]) == 1


@pytest.mark.django_db
def test_cart_update_remove_clear(api_client, variant):
    add = api_client.post(
        "/api/v1/cart/items/",
        {"variant_id": variant.pk, "quantity": 1},
        format="json",
    )
    session = add["X-Cart-Session"]
    item_id = add.data["items"][0]["id"]

    patch = api_client.patch(
        f"/api/v1/cart/items/{item_id}/",
        {"quantity": 3},
        format="json",
        HTTP_X_CART_SESSION=session,
    )
    assert patch.data["item_count"] == 3

    delete = api_client.delete(
        f"/api/v1/cart/items/{item_id}/",
        HTTP_X_CART_SESSION=session,
    )
    assert delete.data["items"] == []

    api_client.post("/api/v1/cart/items/", {"variant_id": variant.pk}, format="json", HTTP_X_CART_SESSION=session)
    cleared = api_client.delete("/api/v1/cart/clear/", HTTP_X_CART_SESSION=session)
    assert cleared.data["items"] == []


@pytest.mark.django_db
def test_quote_submit(api_client, variant, settings):
    settings.CELERY_TASK_ALWAYS_EAGER = True
    settings.CELERY_TASK_EAGER_PROPAGATES = True

    add = api_client.post(
        "/api/v1/cart/items/",
        {"variant_id": variant.pk, "quantity": 1},
        format="json",
    )
    session = add["X-Cart-Session"]

    payload = {
        "contact_name": "Иванов И.И.",
        "company_name": "ООО Тест",
        "email": "buyer@test.ru",
        "phone": "+7 (999) 123-45-67",
        "city": "Москва",
        "inn": "7701234567",
        "privacy_accepted": True,
        "website": "",
    }
    response = api_client.post(
        "/api/v1/quotes/",
        payload,
        format="json",
        HTTP_X_CART_SESSION=session,
    )
    assert response.status_code == 201
    assert response.data["number"].startswith("ЗК-")
    assert QuoteRequest.objects.filter(number=response.data["number"]).exists()

    empty = api_client.get("/api/v1/cart/", HTTP_X_CART_SESSION=session)
    assert empty.data["items"] == []


@pytest.mark.django_db
def test_quote_honeypot(api_client, variant):
    api_client.post("/api/v1/cart/items/", {"variant_id": variant.pk}, format="json")
    response = api_client.post(
        "/api/v1/quotes/",
        {
            "contact_name": "Spam",
            "company_name": "Spam",
            "email": "spam@test.ru",
            "phone": "+79991234567",
            "privacy_accepted": True,
            "website": "http://spam.com",
        },
        format="json",
    )
    assert response.status_code == 400
