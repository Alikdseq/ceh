import pytest

from apps.products.models import Category, ProductGroup, ProductVariant
from apps.products.services.catalog_path_resolve import (
    alternate_group_slugs,
    find_group_by_catalog_segment,
    stale_slug_variants,
)


@pytest.mark.django_db
def test_find_group_by_legacy_6622_slug():
    cat = Category.objects.create(name="КТ", slug="kontaktory-kt-6622")
    child = Category.objects.create(name="6600", slug="kt-6600s", parent=cat)
    group = ProductGroup.objects.create(
        name="КТ6612С/КТ6622С",
        slug="kontaktor-kt-6612-160a-s",
        category=child,
        product_type="KT",
        series_code="6612",
        nominal_current_a=160,
        is_active=True,
    )
    ProductVariant.objects.create(
        group=group,
        sku_code="KT6612S-U3",
        slug="kt6612s-u3",
        execution="S",
        price=100,
        is_default=True,
    )

    found = find_group_by_catalog_segment("kontaktor-kt-6622-160a-s")
    assert found is not None
    assert found.pk == group.pk


@pytest.mark.django_db
def test_find_group_wrong_nominal_6634_resolves_to_250a_s():
    cat = Category.objects.create(name="КТ", slug="kontaktory-kt-6634")
    child = Category.objects.create(name="6600", slug="kt-6600s", parent=cat)
    group = ProductGroup.objects.create(
        name="КТ6634",
        slug="kontaktor-kt-6634-250a-s",
        category=child,
        product_type="KT",
        series_code="6634",
        nominal_current_a=250,
        is_active=True,
    )
    ProductVariant.objects.create(
        group=group,
        sku_code="KT6634S-U3",
        slug="kt6634s-u3",
        execution="S",
        price=100,
        is_default=True,
    )

    found = find_group_by_catalog_segment("kontaktor-kt-6634-160a")
    assert found is not None
    assert found.pk == group.pk
    assert "kontaktor-kt-6634-160a" in stale_slug_variants(group)


@pytest.mark.django_db
def test_alternate_slugs_includes_both_series():
    cat = Category.objects.create(name="K", slug="k-cat")
    group = ProductGroup.objects.create(
        name="КТ6612С/КТ6622С",
        slug="kontaktor-kt-6612-160a-s",
        category=cat,
        product_type="KT",
        series_code="6612",
        nominal_current_a=160,
    )
    ProductVariant.objects.create(
        group=group,
        sku_code="X",
        slug="x",
        execution="S",
        price=1,
    )
    alts = alternate_group_slugs(group)
    assert "kontaktor-kt-6622-160a-s" in alts
    assert "kontaktor-kt-6612-160a-s" in alts
