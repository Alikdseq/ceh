import io

from django.template.loader import render_to_string
from django.utils import timezone

from apps.content.models import PriceListItem, PriceListSection, SiteSettings


def get_price_list_sections():
    return (
        PriceListSection.objects.filter(is_active=True)
        .prefetch_related("items")
        .order_by("sort_order", "name")
    )


def render_price_list_pdf() -> bytes:
    settings = SiteSettings.load()
    sections = []
    for section in get_price_list_sections():
        items = [item for item in section.items.all() if item.is_active]
        if items:
            sections.append({"name": section.name, "items": items})

    context = {
        "company_name": settings.company_name,
        "address": settings.address,
        "phone_main": settings.phone_main,
        "email_main": settings.email_main,
        "sections": sections,
        "generated_at": timezone.localtime(timezone.now()),
        "disclaimer": "Цены указаны с НДС. Не являются публичной офертой.",
    }
    html = render_to_string("content/pricelist_pdf.html", context)
    try:
        from weasyprint import HTML
        return HTML(string=html).write_pdf()
    except Exception:
        from xhtml2pdf import pisa
        buffer = io.BytesIO()
        pisa.CreatePDF(html, dest=buffer)
        return buffer.getvalue()
