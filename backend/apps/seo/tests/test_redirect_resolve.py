import pytest

from apps.seo.models import Redirect
from apps.seo.services.legacy_paths import resolve_legacy_path
from apps.seo.services.redirect_resolve import (
    is_legacy_redirect_candidate,
    paths_equivalent,
    resolve_redirect,
)


def test_paths_equivalent_ignores_trailing_slash():
    assert paths_equivalent("/news", "/news/")
    assert paths_equivalent("/news/", "/news")
    assert not paths_equivalent("/news/", "/partners/")


def test_is_legacy_redirect_candidate_company():
    assert is_legacy_redirect_candidate("/company/news/", "id=98")
    assert not is_legacy_redirect_candidate("/news/")
    assert not is_legacy_redirect_candidate("/partners/")


def test_is_legacy_redirect_candidate_files():
    assert is_legacy_redirect_candidate("/files/cat/foo.doc")
    assert not is_legacy_redirect_candidate("/catalog/kontaktory-kt/")


def test_is_legacy_redirect_candidate_old_catalog():
    assert is_legacy_redirect_candidate("/catalog/contactor/", "id=19")
    assert not is_legacy_redirect_candidate("/catalog/kontaktory-kt/kt-6000b/")


def test_resolve_redirect_canonical_news_not_legacy():
    assert is_legacy_redirect_candidate("/news/") is False


@pytest.mark.django_db
def test_resolve_redirect_no_self_loop_from_db():
    Redirect.objects.create(old_path="/news/", new_path="/news/", is_active=True)
    assert resolve_redirect("/news/") is None


@pytest.mark.django_db
def test_resolve_redirect_db_target():
    Redirect.objects.create(old_path="/old-page/", new_path="/catalog/", is_active=True)
    assert resolve_redirect("/old-page/") == "/catalog/"


def test_resolve_redirect_company_news():
    assert resolve_legacy_path("/company/news/", "id=98") == "/news/"
