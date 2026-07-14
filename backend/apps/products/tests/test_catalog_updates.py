from decimal import Decimal

from apps.core.pricing import price_without_vat, price_without_vat_display
from apps.products.contactor_dimensions import dimensions_for


def test_price_without_vat():
    assert price_without_vat(Decimal("122")) == Decimal("100.00")
    assert price_without_vat_display("7320") == "6000"


def test_kt6013_dimensions():
    dims = dimensions_for("KT", "6013")
    assert dims is not None
    assert dims.l1 == 380
    assert "L1 — 380 мм" in dims.as_spec_value()


def test_ktp6052_l1_override():
    dims = dimensions_for("KTP", "6052")
    assert dims is not None
    assert dims.l1 == 680
