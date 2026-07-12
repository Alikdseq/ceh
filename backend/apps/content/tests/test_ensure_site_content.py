import pytest
from django.core.management import call_command

from apps.content.models import Page


@pytest.mark.django_db
def test_ensure_site_content_seeds_missing_pages():
    assert not Page.objects.filter(slug="about").exists()
    call_command("ensure_site_content")
    assert Page.objects.filter(slug="about", is_published=True).exists()
    assert Page.objects.filter(slug="contacts", is_published=True).exists()
