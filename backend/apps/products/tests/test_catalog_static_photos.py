import pytest
from django.core.files.base import ContentFile
from django.test import Client, override_settings

from apps.products.catalog_static_photos import catalog_tovar_public_path, resolve_product_image_url
from apps.products.models import Category, ProductGroup, ProductImage


@pytest.mark.django_db
def test_catalog_tovar_public_path_finds_ktp6623(tmp_path, settings):
    settings.CATALOG_TOVAR_DIR = tmp_path
    (tmp_path / "КТП6623С.png").write_bytes(b"png")
    path = catalog_tovar_public_path("КТП6623С.png")
    assert path is not None
    assert "/tovar/" in path
    assert "6623" in path


@pytest.mark.django_db
def test_resolve_product_image_url_falls_back_to_tovar(tmp_path, settings):
    settings.CATALOG_TOVAR_DIR = tmp_path
    settings.FRONTEND_URL = "https://www.ekontaktor.ru"
    (tmp_path / "КТП6623С.png").write_bytes(b"png")

    cat = Category.objects.create(name="КТП", slug="ktp-url")
    group = ProductGroup.objects.create(name="КТП6623С", slug="ktp6623-url", category=cat)
    img = ProductImage.objects.create(group=group, image="products/КТП6623С.png")

    url = resolve_product_image_url(img.image)
    assert url is not None
    assert url.startswith("https://www.ekontaktor.ru/tovar/")
    assert "6623" in url


@pytest.mark.django_db
def test_media_url_served_when_file_in_media_root(tmp_path, settings):
    settings.MEDIA_ROOT = tmp_path / "media"
    settings.MEDIA_ROOT.mkdir(parents=True)
    products = settings.MEDIA_ROOT / "products"
    products.mkdir()
    (products / "test.png").write_bytes(b"\x89PNG")

    client = Client()
    response = client.get("/media/products/test.png")
    assert response.status_code == 200
    body = b"".join(response.streaming_content)
    assert body.startswith(b"\x89PNG")


@pytest.mark.django_db
def test_resolve_uses_media_when_synced(tmp_path, settings):
    settings.MEDIA_ROOT = tmp_path / "media"
    settings.CATALOG_TOVAR_DIR = tmp_path / "tovar"
    settings.CATALOG_TOVAR_DIR.mkdir()
    settings.FRONTEND_URL = "https://www.ekontaktor.ru"
    (settings.MEDIA_ROOT / "products").mkdir(parents=True)
    (settings.MEDIA_ROOT / "products" / "КТП6623С.png").write_bytes(b"synced")

    cat = Category.objects.create(name="K", slug="k-sync")
    group = ProductGroup.objects.create(name="K", slug="k-sync-g", category=cat)
    img = ProductImage.objects.create(group=group, image="products/КТП6623С.png")

    url = resolve_product_image_url(img.image)
    assert "/media/products/" in url
