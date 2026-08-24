import pytest

from apps.products.models import Category, ProductGroup, ProductImage


@pytest.mark.django_db
def test_seed_product_images_from_catalog(tmp_path, settings):
    settings.CATALOG_TOVAR_DIR = tmp_path
    (tmp_path / "КТ6052Б.png").write_bytes(b"png")

    cat = Category.objects.create(name="КТ", slug="kt-seed")
    group = ProductGroup.objects.create(
        name="КТ6052Б",
        slug="kt6052b-seed",
        category=cat,
        product_type="KT",
        series_code="6052",
    )
    assert not group.images.exists()

    from django.core.management import call_command

    call_command("seed_product_images_from_catalog")

    group.refresh_from_db()
    assert group.images.count() == 1
    img = group.images.get()
    assert "6052" in img.image.name
    assert img.is_primary is True


@pytest.mark.django_db
def test_seed_skips_when_cms_exists(tmp_path, settings):
    settings.CATALOG_TOVAR_DIR = tmp_path
    (tmp_path / "КТ6052Б.png").write_bytes(b"png")

    cat = Category.objects.create(name="КТ", slug="kt-seed-skip")
    group = ProductGroup.objects.create(
        name="КТ6052Б",
        slug="kt6052b-seed-skip",
        category=cat,
        product_type="KT",
        series_code="6052",
    )
    ProductImage.objects.create(group=group, image="products/existing.png", is_primary=True)

    from django.core.management import call_command

    call_command("seed_product_images_from_catalog")

    assert group.images.count() == 1
