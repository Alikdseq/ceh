import pytest
from django.test import RequestFactory
from django.test.utils import override_settings

from apps.core.middleware import SecurityHeadersMiddleware


@pytest.fixture
def middleware_response():
    factory = RequestFactory()
    request = factory.get("/")

    def get_response(req):
        from django.http import HttpResponse
        return HttpResponse("ok")

    return SecurityHeadersMiddleware(get_response), request


@override_settings(DEBUG=False)
def test_csp_header_in_production(middleware_response):
    mw, request = middleware_response
    response = mw(request)
    assert "Content-Security-Policy" in response
    assert "mc.yandex.ru" in response["Content-Security-Policy"]
    assert "unsafe-eval" not in response["Content-Security-Policy"]


@override_settings(DEBUG=False, ADMIN_URL="manage/")
def test_csp_skipped_on_admin():
    factory = RequestFactory()
    request = factory.get("/manage/products/productgroup/1/change/")

    def get_response(req):
        from django.http import HttpResponse
        return HttpResponse("ok")

    response = SecurityHeadersMiddleware(get_response)(request)
    assert "Content-Security-Policy" not in response


@override_settings(DEBUG=True)
def test_csp_skipped_in_debug(middleware_response):
    mw, request = middleware_response
    response = mw(request)
    assert "Content-Security-Policy" not in response


@override_settings(DEBUG=False)
def test_permissions_policy_header(middleware_response):
    mw, request = middleware_response
    response = mw(request)
    assert "Permissions-Policy" in response
