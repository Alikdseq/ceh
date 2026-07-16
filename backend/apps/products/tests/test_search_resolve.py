import pytest

from apps.products.models import Category, ProductGroup, ProductVariant
from apps.products.services.search import resolve_search_to_product


@pytest.mark.django_db
def test_resolve_search_kt6023_single_group():
    cat = Category.objects.create(name="КТ", slug="kontaktory-kt")
    child = Category.objects.create(name="6000", slug="kt-6000b", parent=cat)
    group = ProductGroup.objects.create(
        name="КТ6023Б",
        slug="kontaktor-kt-6023-160a-b",
        category=child,
        product_type="KT",
        series_code="6023",
        nominal_current_a=160,
        is_active=True,
    )
    ProductVariant.objects.create(
        group=group,
        sku_code="KT6023B-U3",
        slug="kt6023b-u3",
        execution="B",
        price=100,
        is_default=True,
    )

    hit = resolve_search_to_product("кт6023")
    assert hit is not None
    assert hit.pk == group.pk
