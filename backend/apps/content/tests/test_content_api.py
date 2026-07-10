import pytest
from django.utils import timezone
from rest_framework.test import APIClient

from apps.content.models import FAQItem, NewsPost, Page, SiteSettings


@pytest.fixture
def api_client():
    return APIClient()


@pytest.mark.django_db
def test_site_settings_api(api_client):
    settings_obj = SiteSettings.load()
    settings_obj.company_name = "Электроконтактор"
    settings_obj.save()
    response = api_client.get("/api/v1/settings/")
    assert response.status_code == 200
    assert response.data["company_name"] == "Электроконтактор"


@pytest.mark.django_db
def test_page_detail(api_client):
    Page.objects.create(title="Контакты", slug="contacts", body="<p>addr</p>", is_published=True)
    response = api_client.get("/api/v1/pages/contacts/")
    assert response.status_code == 200
    assert response.data["h1"] or response.data["title"]


@pytest.mark.django_db
def test_page_not_found(api_client):
    response = api_client.get("/api/v1/pages/missing/")
    assert response.status_code == 404


@pytest.mark.django_db
def test_news_list(api_client):
    NewsPost.objects.create(
        title="A", slug="a", excerpt="e", body="b",
        is_published=True, published_at=timezone.now(),
    )
    response = api_client.get("/api/v1/news/")
    assert response.status_code == 200
    assert len(response.data["results"]) >= 1


@pytest.mark.django_db
def test_news_detail(api_client):
    NewsPost.objects.create(
        title="A", slug="a", excerpt="e", body="body",
        is_published=True, published_at=timezone.now(),
    )
    response = api_client.get("/api/v1/news/a/")
    assert response.status_code == 200
    assert "body" in response.data


@pytest.mark.django_db
def test_faq_list(api_client):
    FAQItem.objects.create(category="general", question="Q?", answer="A")
    response = api_client.get("/api/v1/faq/")
    assert response.status_code == 200
    assert len(response.data) >= 1


@pytest.mark.django_db
def test_news_rss(api_client):
    NewsPost.objects.create(
        title="RSS", slug="rss", excerpt="e", body="b",
        is_published=True, published_at=timezone.now(),
    )
    response = api_client.get("/api/v1/news/rss/")
    assert response.status_code == 200
    assert b"rss" in response.content.lower() or b"RSS" in response.content
