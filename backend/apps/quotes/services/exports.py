import io
from decimal import Decimal

from django.template.loader import render_to_string
from django.utils import timezone

from apps.content.models import SiteSettings

from ..models import QuoteCart
from .cart import cart_subtotal, get_cart_queryset


def _cart_context(cart: QuoteCart) -> dict:
    settings = SiteSettings.load()
    items = []
    for item in get_cart_queryset(cart):
        items.append({
            "sku_code": item.variant.sku_code,
            "product_name": item.variant.group.name,
            "unit_price": item.unit_price_snapshot,
            "quantity": item.quantity,
            "line_total": item.line_total,
        })
    return {
        "company_name": settings.company_name,
        "address": settings.address,
        "requisites": settings.requisites,
        "phone_main": settings.phone_main,
        "email_main": settings.email_main,
        "items": items,
        "subtotal": cart_subtotal(cart),
        "vat_included": True,
        "generated_at": timezone.localtime(timezone.now()),
        "disclaimer": "Цены указаны с НДС. Не являются публичной офертой.",
    }


def render_cart_pdf(cart: QuoteCart) -> bytes:
    html = render_to_string("quotes/cart_pdf.html", _cart_context(cart))
    try:
        from weasyprint import HTML
        return HTML(string=html).write_pdf()
    except Exception:
        from xhtml2pdf import pisa
        buffer = io.BytesIO()
        pisa.CreatePDF(html, dest=buffer)
        return buffer.getvalue()


def render_quote_pdf(quote) -> bytes:
    settings = SiteSettings.load()
    context = {
        "company_name": settings.company_name,
        "address": settings.address,
        "requisites": settings.requisites,
        "phone_main": settings.phone_main,
        "email_main": settings.email_main,
        "quote": quote,
        "items": quote.items.all(),
        "subtotal": quote.subtotal,
        "vat_included": quote.vat_included,
        "generated_at": timezone.localtime(quote.created_at),
        "disclaimer": "Цены указаны с НДС. Не являются публичной офертой.",
    }
    html = render_to_string("quotes/quote_pdf.html", context)
    try:
        from weasyprint import HTML
        return HTML(string=html).write_pdf()
    except Exception:
        from xhtml2pdf import pisa
        buffer = io.BytesIO()
        pisa.CreatePDF(html, dest=buffer)
        return buffer.getvalue()


def render_cart_xlsx(cart: QuoteCart) -> bytes:
    from openpyxl import Workbook
    from openpyxl.styles import Font

    wb = Workbook()
    ws = wb.active
    ws.title = "Спецификация"
    headers = ["№", "Артикул", "Наименование", "Цена, ₽", "Кол-во", "Сумма, ₽"]
    ws.append(headers)
    for cell in ws[1]:
        cell.font = Font(bold=True)

    for idx, item in enumerate(get_cart_queryset(cart), start=1):
        ws.append([
            idx,
            item.variant.sku_code,
            item.variant.group.name,
            float(item.unit_price_snapshot),
            item.quantity,
            float(item.line_total),
        ])

    subtotal = cart_subtotal(cart)
    ws.append(["", "", "", "", "ИТОГО:", float(subtotal)])
    ws.append([])
    ws.append(["", "", "Цены указаны с НДС. Не являются публичной офертой."])

    buffer = io.BytesIO()
    wb.save(buffer)
    return buffer.getvalue()
