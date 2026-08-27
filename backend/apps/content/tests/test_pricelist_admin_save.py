from django.conf import settings


def test_data_upload_max_number_fields_raised_for_large_pricelist():
    """Pricelist sections with 120+ inline rows exceed Django default of 1000."""
    assert settings.DATA_UPLOAD_MAX_NUMBER_FIELDS >= 5000
