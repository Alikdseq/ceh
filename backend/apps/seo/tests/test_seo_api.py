import pytest
from django.core.management import call_command
from django.utils import timezone
from rest_framework.test import APIClient

from apps.content.models import NewsPost, Page
from apps.products.models import Category, ProductGroup, ProductVariant
from apps.seo.models import Redirect
from apps.seo.services.sitemap import build_robots_txt, build_sitemap_xml, collect_urls


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def catalog_for_sitemap(db):
    root = Category.objects.create(name="Контакторы КТ", slug="kontaktory-kt")
    child = Category.objects.create(name="Серия 6000", slug="kt-6000", parent=root)
    group = ProductGroup.objects.create(
        name="Контактор КТ 6043",
        slug="kontaktor-kt-6043",
        category=child,
        product_type="KT",
        nominal_current_a=400,
    )
    ProductVariant.objects.create(
        group=group, sku_code="KT6043B", slug="kt6043b", execution="B", price=100, is_default=True,
    )
    NewsPost.objects.create(
        title="Новость", slug="news-1", excerpt="e", body="b",
        is_published=True, published_at=timezone.now(),
    )
    Page.objects.create(title="О заводе", slug="about", body="x", is_published=True)
    return group


@pytest.mark.django_db
def test_sitemap_xml_contains_product(catalog_for_sitemap):
    xml = build_sitemap_xml().decode("utf-8")
    assert "kontaktor-kt-6043" in xml
    assert "kontaktory-kt/kt-6000/kontaktor-kt-6043" in xml
    assert "<?xml" in xml


@pytest.mark.django_db
def test_sitemap_xml_excludes_search():
    xml = build_sitemap_xml().decode("utf-8")
    assert "/search/" not in xml


@pytest.mark.django_db
def test_robots_txt_disallows_search():
    text = build_robots_txt()
    assert "Disallow: /search" in text


@pytest.mark.django_db
def test_sitemap_xml_contains_news(catalog_for_sitemap):
    xml = build_sitemap_xml().decode("utf-8")
    assert "/news/news-1" in xml


@pytest.mark.django_db
def test_sitemap_xml_contains_category(catalog_for_sitemap):
    xml = build_sitemap_xml().decode("utf-8")
    assert "kontaktory-kt" in xml


@pytest.mark.django_db
def test_collect_urls_includes_static():
    urls = collect_urls()
    locs = {u["loc"] for u in urls}
    assert any(u.endswith("/catalog/") for u in locs)


@pytest.mark.django_db
def test_robots_txt_disallows_manage():
    text = build_robots_txt()
    assert "Disallow: /manage/" in text
    assert "Disallow: /api/" in text
    assert "Sitemap:" in text


@pytest.mark.django_db
def test_sitemap_api(api_client, catalog_for_sitemap):
    response = api_client.get("/api/v1/seo/sitemap.xml")
    assert response.status_code == 200
    assert b"kontaktor-kt-6043" in response.content


@pytest.mark.django_db
def test_robots_api(api_client):
    response = api_client.get("/api/v1/seo/robots.txt")
    assert response.status_code == 200
    assert b"Disallow: /manage/" in response.content


@pytest.mark.django_db
def test_redirect_resolve_found(api_client):
    Redirect.objects.create(old_path="/old/", new_path="/catalog/", is_active=True)
    response = api_client.get("/api/v1/redirects/resolve/", {"path": "/old/"})
    assert response.status_code == 200
    assert response.data["new_path"] == "/catalog/"


@pytest.mark.django_db
def test_redirect_resolve_missing(api_client):
    response = api_client.get("/api/v1/redirects/resolve/", {"path": "/missing/"})
    assert response.status_code == 200
    assert response.data["new_path"] is None


@pytest.mark.django_db
def test_redirect_resolve_legacy_company_news(api_client):
    response = api_client.get(
        "/api/v1/redirects/resolve/",
        {"path": "/company/news/", "query": "id=98"},
    )
    assert response.status_code == 200
    assert response.data["new_path"] == "/news/"


@pytest.mark.django_db
def test_redirect_resolve_legacy_files_doc(api_client):
    response = api_client.get(
        "/api/v1/redirects/resolve/",
        {"path": "/files/cat/_________________-4.doc"},
    )
    assert response.status_code == 200
    assert response.data["new_path"] == "/catalog/"


@pytest.mark.django_db
def test_redirect_resolve_no_self_loop(api_client):
    Redirect.objects.create(old_path="/news/", new_path="/news/", is_active=True)
    response = api_client.get("/api/v1/redirects/resolve/", {"path": "/news/"})
    assert response.status_code == 200
    assert response.data["new_path"] is None


@pytest.mark.django_db
def test_redirect_resolve_canonical_pages_no_redirect(api_client):
    for path in ("/news/", "/partners/", "/catalog/", "/about/"):
        response = api_client.get("/api/v1/redirects/resolve/", {"path": path})
        assert response.status_code == 200
        assert response.data["new_path"] is None, path


@pytest.mark.django_db
def test_import_redirects_command(tmp_path, db):
    csv_file = tmp_path / "redirects.csv"
    csv_file.write_text("old_path,new_path\n/test-old/,/catalog/\n", encoding="utf-8")
    call_command("import_redirects", str(csv_file))
    assert Redirect.objects.filter(old_path="/test-old/").exists()


@pytest.mark.django_db
def test_generate_sitemap_command(catalog_for_sitemap, settings, tmp_path):
    settings.MEDIA_ROOT = tmp_path
    call_command("generate_sitemap")
    assert (tmp_path / "sitemap.xml").exists()
