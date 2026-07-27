import io

from django.template.loader import render_to_string
from django.utils import timezone

from apps.content.models import PriceListItem, PriceListSection, SiteSettings
from apps.core.pricing import price_without_vat_display


def _serialize_item(item: PriceListItem) -> dict:
    return {
        "name": item.name,
        "nominal_current_a": item.nominal_current_a,
        "notes": item.notes,
        "price": item.price,
        "price_without_vat": price_without_vat_display(item.price),
    }


def get_price_list_sections():
    return (
        PriceListSection.objects.filter(is_active=True)
        .prefetch_related("items")
        .order_by("sort_order", "name")
    )


def merge_duplicate_pricelist_sections() -> int:
    """Merge sections with the same name (e.g. after Аксессуары → Комплектующие rename)."""
    merged = 0
    sections = list(PriceListSection.objects.all().order_by("sort_order", "pk"))
    by_name: dict[str, list[PriceListSection]] = {}
    for section in sections:
        by_name.setdefault(section.name.strip(), []).append(section)

    for group in by_name.values():
        if len(group) <= 1:
            continue
        primary = group[0]
        for duplicate in group[1:]:
            for item in duplicate.items.all():
                existing = PriceListItem.objects.filter(
                    section=primary,
                    name=item.name,
                ).first()
                if existing:
                    existing.price = item.price
                    existing.nominal_current_a = item.nominal_current_a
                    existing.product_type = item.product_type
                    existing.notes = item.notes
                    existing.sort_order = item.sort_order
                    existing.is_active = item.is_active
                    existing.save()
                    item.delete()
                else:
                    item.section = primary
                    item.save(update_fields=["section"])
            duplicate.delete()
            merged += 1
    return merged


def render_price_list_pdf() -> bytes:
    settings = SiteSettings.load()
    sections = []
    for section in get_price_list_sections():
        items = [_serialize_item(item) for item in section.items.all() if item.is_active]
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
