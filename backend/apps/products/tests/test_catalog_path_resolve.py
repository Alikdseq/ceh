import pytest

from apps.products.models import Category
from apps.products.services.catalog_path_resolve import collect_category_redirects


@pytest.mark.django_db
def test_collect_category_redirects_short_paths():
    root = Category.objects.create(name="Контакторы КТ", slug="kontaktory-kt", is_active=True)
    Category.objects.create(
        name="КТ 6000",
        slug="kt-6000b",
        parent=root,
        is_active=True,
    )

    pairs = dict(collect_category_redirects())
    assert "/catalog/kt-6000b/" in pairs
    assert pairs["/catalog/kt-6000b/"] == "/catalog/kontaktory-kt/kt-6000b/"
