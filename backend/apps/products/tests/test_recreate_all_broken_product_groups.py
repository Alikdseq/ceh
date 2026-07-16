import pytest
from django.core.management import call_command

from apps.products.models import Category, ProductGroup, ProductImage


@pytest.mark.django_db
def test_recreate_all_broken_product_groups_dry_run():
    cat = Category.objects.create(name="C", slug="c-all-broken")
    g1 = ProductGroup.objects.create(name="G1", slug="g1-broken", category=cat)
    g2 = ProductGroup.objects.create(name="G2", slug="g2-ok", category=cat)
    ProductImage.objects.create(group=g1, image="products/missing1.png")
    ProductImage.objects.create(group=g2, image="products/missing2.png")

    call_command("recreate_all_broken_product_groups", "--dry-run")

    assert ProductGroup.objects.filter(pk=g1.pk).exists()
    assert ProductGroup.objects.filter(pk=g2.pk).exists()


@pytest.mark.django_db
def test_recreate_all_broken_product_groups_applies():
    cat = Category.objects.create(name="C2", slug="c-all-broken2")
    group = ProductGroup.objects.create(name="G", slug="g-bulk", category=cat)
    ProductImage.objects.create(group=group, image="products/missing-bulk.png")
    old_pk = group.pk

    call_command("recreate_all_broken_product_groups")

    assert not ProductGroup.objects.filter(pk=old_pk).exists()
    new_group = ProductGroup.objects.get(slug="g-bulk")
    assert new_group.pk != old_pk
    assert new_group.images.count() == 0
