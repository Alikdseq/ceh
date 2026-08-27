import pytest
from decimal import Decimal

from apps.content.admin_forms import PriceListItemAdminForm
from apps.content.models import PriceListItem, PriceListSection


@pytest.mark.django_db
def test_pricelist_form_accepts_comma_decimal_price():
    section = PriceListSection.objects.create(name="КТ", sort_order=0)
    form = PriceListItemAdminForm(
        data={
            "section": section.pk,
            "name": "КТП6633С 3з+3р (250А)",
            "price": "22 238,00",
            "nominal_current_a": "250",
            "notes": "С — силовые контакты",
            "sort_order": "119",
            "is_active": "on",
            "product_type": "",
        }
    )
    assert form.is_valid(), form.errors
    item = form.save()
    assert item.price == Decimal("22238.00")


@pytest.mark.django_db
def test_pricelist_form_skips_blank_inline_row():
    section = PriceListSection.objects.create(name="КТ", sort_order=0)
    form = PriceListItemAdminForm(
        data={
            "section": section.pk,
            "name": "",
            "price": "0",
            "sort_order": "0",
            "is_active": "on",
            "product_type": "",
            "notes": "",
        }
    )
    assert not form.has_changed()
