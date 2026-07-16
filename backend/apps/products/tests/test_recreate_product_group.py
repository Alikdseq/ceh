import pytest
from django.core.management import call_command
from django.core.management.base import CommandError

from apps.products.models import Category, ProductGroup, ProductImage, ProductSpec, ProductVariant


@pytest.mark.django_db
def test_recreate_product_group_keeps_slug_and_variants():
    cat = Category.objects.create(name="КТП", slug="ktp-recreate-cat")
    group = ProductGroup.objects.create(
        name="КТП6623С",
        slug="ktp6623s-test",
        category=cat,
        product_type="KTP",
        series_code="6623",
        image_rotation=270,
    )
    ProductVariant.objects.create(
        group=group,
        sku_code="KTP6623S-220",
        slug="ktp6623s-220",
        execution="S",
        coil_voltage_v=220,
        price=100,
        is_default=True,
    )
    ProductSpec.objects.create(
        group=group,
        spec_key="nominal_current",
        spec_value="160",
        spec_unit="А",
    )
    ProductImage.objects.create(group=group, image="products/missing.png", is_primary=True)

    old_pk = group.pk
    call_command("recreate_product_group", slug="ktp6623s-test")

    assert not ProductGroup.objects.filter(pk=old_pk).exists()
    new_group = ProductGroup.objects.get(slug="ktp6623s-test")
    assert new_group.pk != old_pk
    assert new_group.image_rotation == 270
    assert new_group.variants.count() == 1
    assert new_group.specs.count() == 1
    assert new_group.images.count() == 0


@pytest.mark.django_db
def test_recreate_requires_selector():
    with pytest.raises(CommandError):
        call_command("recreate_product_group")
