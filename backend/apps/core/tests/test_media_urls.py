from django.test import override_settings

from apps.core.media_urls import public_media_url


@override_settings(FRONTEND_URL="https://www.ekontaktor.ru")
def test_rewrites_backend_host():
    url = public_media_url("http://backend:8000/media/products/x.jpg", request=None)
    assert url == "https://www.ekontaktor.ru/media/products/x.jpg"


@override_settings(FRONTEND_URL="https://www.ekontaktor.ru")
def test_relative_media_uses_frontend():
    assert public_media_url("/media/products/a.jpg") == "https://www.ekontaktor.ru/media/products/a.jpg"


@override_settings(FRONTEND_URL="https://www.ekontaktor.ru")
def test_external_url_unchanged():
    url = "https://cdn.example.com/img.jpg"
    assert public_media_url(url) == url
