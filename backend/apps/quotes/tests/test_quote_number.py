import pytest
from apps.quotes.models import QuoteRequest, generate_quote_number


@pytest.mark.django_db
def test_generate_quote_number_first():
    number = generate_quote_number()
    year = number.split("-")[1]
    assert number.startswith(f"ЗК-{year}-")
    assert number.endswith("00001")


@pytest.mark.django_db
def test_generate_quote_number_sequential():
    QuoteRequest.objects.create(
        number=generate_quote_number(),
        contact_name="Test",
        company_name="Test Co",
        email="test@test.ru",
        phone="+79991234567",
    )
    second = generate_quote_number()
    assert second.endswith("00002")
