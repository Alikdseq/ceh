import pytest

from apps.seo.services.legacy_paths import normalize_legacy_path, paths_equivalent, resolve_legacy_path


def test_normalize_legacy_path_adds_trailing_slash():
    assert normalize_legacy_path("/news") == "/news/"
    assert normalize_legacy_path("/company/news?id=98") == "/company/news/"


def test_paths_equivalent():
    assert paths_equivalent("/news", "/news/")
    assert not paths_equivalent("/news/", "/partners/")


def test_company_news_with_id_redirects_to_news():
    target = resolve_legacy_path("/company/news/", "id=98")
    assert target == "/news/"


def test_company_dilers_redirects_to_partners():
    assert resolve_legacy_path("/company/dilers/") == "/partners/"


def test_company_contact_redirects_to_contacts():
    assert resolve_legacy_path("/company/contact/") == "/contacts/"


def test_files_cat_doc_redirects_to_catalog():
    assert resolve_legacy_path("/files/cat/_________________-4.doc") == "/catalog/"


def test_catalog_contactor_id_19():
    assert resolve_legacy_path("/catalog/contactor/", "id=19") == "/catalog/kontaktory-kt/kt-6000b/"


def test_catalog_switch_id_50():
    assert resolve_legacy_path("/catalog/switch/", "id=50") == (
        "/catalog/vyklyuchateli/vyklyuchateli-putevye/vpk-3110/"
    )


def test_canonical_paths_do_not_self_redirect():
    assert resolve_legacy_path("/news/") is None
    assert resolve_legacy_path("/partners/") is None
    assert resolve_legacy_path("/catalog/") is None
