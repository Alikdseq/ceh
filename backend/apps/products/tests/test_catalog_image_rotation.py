import pytest

from apps.products.catalog_image_rotation import should_rotate_product_group
from apps.products.models import Category, ProductGroup, ProductVariant


@pytest.mark.django_db
def test_listed_rotation_matches_kt6043b():
    cat = Category.objects.create(name="КТ", slug="kt-rot-test")
    group = ProductGroup.objects.create(
        name="КТ6043Б-У3",
        slug="kt6043b-listed",
        category=cat,
        product_type="KT",
        series_code="6043",
    )
    ProductVariant.objects.create(
        group=group,
        sku_code="КТ6043Б-У3",
        slug="kt6043b-u3",
        execution="B",
        coil_voltage_v=220,
        is_default=True,
    )
    assert should_rotate_product_group(group) is True


@pytest.mark.django_db
def test_listed_rotation_skips_kt6053b():
    cat = Category.objects.create(name="КТ", slug="kt-rot-test-2")
    group = ProductGroup.objects.create(
        name="КТ6053Б-У3",
        slug="kt6053b-not-listed",
        category=cat,
        product_type="KT",
        series_code="6053",
    )
    ProductVariant.objects.create(
        group=group,
        sku_code="КТ6053Б-У3",
        slug="kt6053b-u3",
        execution="B",
        is_default=True,
    )
    assert should_rotate_product_group(group) is False
