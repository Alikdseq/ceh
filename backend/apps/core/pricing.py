"""VAT helpers — catalog prices are stored with VAT included."""

from decimal import Decimal, ROUND_HALF_UP

VAT_RATE = Decimal("0.22")


def price_without_vat(price_with_vat) -> Decimal:
    gross = Decimal(str(price_with_vat or 0))
    if gross <= 0:
        return gross
    return (gross / (Decimal("1") + VAT_RATE)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def price_without_vat_display(price_with_vat) -> str:
    net = price_without_vat(price_with_vat)
    if net <= 0:
        return "0"
    return str(net.quantize(Decimal("1"), rounding=ROUND_HALF_UP))
