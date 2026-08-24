import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient

from apps.products.admin_helpers import ProductImageAdminForm
from apps.products.models import Category, ProductGroup, ProductImage


@pytest.fixture
def api_client():
    return APIClient()


@pytest.mark.django_db
def test_categories_api_includes_image_url(api_client):
    category = Category.objects.create(name="КТ", slug="kontaktory-kt-api")
    category.image.save(
        "kt.png",
        SimpleUploadedFile("kt.png", b"\x89PNG\r\n\x1a\n", content_type="image/png"),
        save=True,
    )

    response = api_client.get("/api/v1/categories/")
    assert response.status_code == 200
    root = next(item for item in response.data if item["slug"] == "kontaktory-kt-api")
    assert root["image_url"]
    assert "/media/" in root["image_url"]


@pytest.mark.django_db
def test_product_image_admin_form_allows_empty_extra_row():
    cat = Category.objects.create(name="КТ", slug="kt-img-form")
    group = ProductGroup.objects.create(name="КТ6012", slug="kt6012-img", category=cat, product_type="KT")

    form = ProductImageAdminForm(
        data={
            "image": "",
            "alt": "",
            "sort_order": "0",
            "is_primary": "",
        },
        instance=ProductImage(group=group),
    )
    assert form.is_valid(), form.errors
