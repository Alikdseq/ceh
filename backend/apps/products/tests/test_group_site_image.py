import pytest

from apps.products.group_site_image import primary_image_payload, resolve_group_site_image
from apps.products.models import Category, ProductGroup, ProductImage
from apps.products.static_product_images import resolve_static_product_image_for_group


@pytest.mark.django_db
def test_resolve_static_for_kt6052():
    cat = Category.objects.create(name="КТ", slug="kt-static")
    group = ProductGroup.objects.create(
        name="КТ6052Б",
        slug="kt6052b",
        category=cat,
        product_type="KT",
        series_code="6052",
    )
    url = resolve_static_product_image_for_group(group)
    assert url is not None
    assert "6052" in url


@pytest.mark.django_db
def test_primary_image_prefers_cms_over_static(tmp_path, settings):
    settings.MEDIA_ROOT = tmp_path / "media"
    (settings.MEDIA_ROOT / "products").mkdir(parents=True)
    (settings.MEDIA_ROOT / "products" / "custom.png").write_bytes(b"png")
    settings.FRONTEND_URL = "https://www.ekontaktor.ru"

    cat = Category.objects.create(name="КТ", slug="kt-cms")
    group = ProductGroup.objects.create(
        name="КТ6052Б",
        slug="kt6052b-cms",
        category=cat,
        product_type="KT",
        series_code="6052",
    )
    ProductImage.objects.create(group=group, image="products/custom.png", is_primary=True)

    payload = primary_image_payload(group)
    assert payload["is_placeholder"] is False
    assert payload["source"] == "cms"
    assert "/media/products/custom.png" in payload["url"]


@pytest.mark.django_db
def test_primary_image_static_when_no_cms():
    cat = Category.objects.create(name="КТ", slug="kt-static-api")
    group = ProductGroup.objects.create(
        name="КТ6052Б",
        slug="kt6052b-static",
        category=cat,
        product_type="KT",
        series_code="6052",
    )
    payload = primary_image_payload(group)
    assert payload["is_placeholder"] is True
    assert payload["source"] == "static"
    assert "6052" in payload["url"]


@pytest.mark.django_db
def test_admin_site_image_shows_static(tmp_path, settings):
    settings.CATALOG_TOVAR_DIR = tmp_path
    (tmp_path / "КТ6052Б.png").write_bytes(b"png")
    settings.FRONTEND_URL = "https://www.ekontaktor.ru"

    cat = Category.objects.create(name="КТ", slug="kt-admin-static")
    group = ProductGroup.objects.create(
        name="КТ6052Б",
        slug="kt6052b-admin",
        category=cat,
        product_type="KT",
        series_code="6052",
    )
    site = resolve_group_site_image(group)
    assert site["source"] == "static"
    assert "6052" in site["url"]
