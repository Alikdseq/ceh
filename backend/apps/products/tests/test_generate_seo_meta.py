import pytest
from django.core.management import call_command

from apps.products.models import Category, ProductGroup


@pytest.mark.django_db
def test_generate_seo_meta_fills_empty_fields():
    cat = Category.objects.create(name="Контакторы КТ", slug="kontaktory-kt")
    group = ProductGroup.objects.create(
        name="Контактор КТ 6043",
        slug="kontaktor-kt-6043",
        category=cat,
        nominal_current_a=400,
        poles=3,
    )
    call_command("generate_seo_meta", "--categories", "--products")
    cat.refresh_from_db()
    group.refresh_from_db()
    assert cat.meta_title
    assert cat.meta_description
    assert group.meta_title
    assert group.meta_description
    assert "6043" in group.meta_title or "КТ" in group.meta_title


@pytest.mark.django_db
def test_generate_seo_meta_dry_run():
    Category.objects.create(name="Test", slug="test-cat")
    call_command("generate_seo_meta", "--categories", "--dry-run")
