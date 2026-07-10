import pytest

from apps.quotes.models import QuoteCart, QuoteCartItem, QuoteRequest, generate_quote_number
from apps.products.models import Category, ProductGroup, ProductVariant


@pytest.fixture
def variant(db):
    cat = Category.objects.create(name="C", slug="c")
    group = ProductGroup.objects.create(name="G", slug="g", category=cat, product_type="KT")
    return ProductVariant.objects.create(
        group=group, sku_code="SKU", slug="sku", execution="B", price=100, is_default=True,
    )


@pytest.mark.django_db
def test_quote_request_str():
    q = QuoteRequest.objects.create(
        number="ЗК-2026-00001",
        contact_name="Ivan",
        company_name="Co",
        email="a@b.ru",
        phone="+7999",
    )
    assert "ЗК-2026-00001" in str(q)


@pytest.mark.django_db
def test_quote_cart_session_key():
    cart = QuoteCart.objects.create(session_key="abc123")
    assert cart.session_key == "abc123"


@pytest.mark.django_db
def test_quote_cart_item_subtotal(variant):
    cart = QuoteCart.objects.create(session_key="sess")
    item = QuoteCartItem.objects.create(cart=cart, variant=variant, quantity=3)
    assert item.quantity == 3


@pytest.mark.django_db
def test_generate_quote_number_format():
    number = generate_quote_number()
    parts = number.split("-")
    assert parts[0] == "ЗК"
    assert len(parts) == 3


@pytest.mark.django_db
def test_quote_request_utm_fields():
    q = QuoteRequest.objects.create(
        number=generate_quote_number(),
        contact_name="Ivan",
        company_name="Co",
        email="a@b.ru",
        phone="+7999",
        utm_source="google",
        utm_medium="cpc",
    )
    assert q.utm_source == "google"
    assert q.utm_medium == "cpc"


@pytest.mark.django_db
def test_quote_cart_item_cascade_delete(variant):
    cart = QuoteCart.objects.create(session_key="sess2")
    QuoteCartItem.objects.create(cart=cart, variant=variant, quantity=1)
    cart.delete()
    assert QuoteCartItem.objects.count() == 0
