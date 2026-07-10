from unittest.mock import patch

import pytest
from django.test import override_settings

from apps.seo.services.indexnow import submit_indexnow_urls


@pytest.mark.django_db
def test_indexnow_skipped_when_disabled():
    result = submit_indexnow_urls(["/catalog/"])
    assert result.get("skipped") is True


@override_settings(INDEXNOW_ENABLED=True, INDEXNOW_KEY="test-key-123", FRONTEND_URL="https://ekontaktor.ru")
def test_indexnow_submits_when_enabled():
    with patch("apps.seo.services.indexnow.urllib.request.urlopen") as mock_urlopen:
        mock_urlopen.return_value.__enter__.return_value.status = 200
        result = submit_indexnow_urls(["/catalog/kontaktory-kt/"])
    assert result.get("skipped") is not True
    assert result.get("submitted") == 1
    assert mock_urlopen.call_count == 2
