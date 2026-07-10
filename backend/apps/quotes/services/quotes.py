from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from apps.content.models import SiteSettings

from ..models import QuoteCart, QuoteRequest, QuoteRequestItem
from .cart import cart_subtotal, clear_cart, get_cart_queryset


@transaction.atomic
def create_quote_from_cart(
    cart: QuoteCart,
    *,
    contact_name: str,
    company_name: str,
    email: str,
    phone: str,
    city: str = "",
    inn: str = "",
    kpp: str = "",
    comment: str = "",
    ip: str | None = None,
    user_agent: str = "",
    utm_source: str = "",
    utm_medium: str = "",
    utm_campaign: str = "",
) -> QuoteRequest:
    items = list(get_cart_queryset(cart))
    if not items:
        raise ValueError("empty_cart")

    subtotal = cart_subtotal(cart)
    quote = QuoteRequest.objects.create(
        contact_name=contact_name,
        company_name=company_name,
        email=email,
        phone=phone,
        city=city,
        inn=inn,
        kpp=kpp,
        comment=comment,
        subtotal=subtotal,
        vat_included=True,
        ip=ip,
        user_agent=user_agent,
        utm_source=utm_source,
        utm_medium=utm_medium,
        utm_campaign=utm_campaign,
        status=QuoteRequest.Status.NEW,
    )

    QuoteRequestItem.objects.bulk_create([
        QuoteRequestItem(
            request=quote,
            sku_code=item.variant.sku_code,
            product_name=item.variant.group.name,
            unit_price=item.unit_price_snapshot,
            quantity=item.quantity,
            line_total=Decimal(item.unit_price_snapshot * item.quantity),
        )
        for item in items
    ])

    clear_cart(cart)
    return quote


def get_order_recipients() -> list[str]:
    settings = SiteSettings.load()
    emails = settings.get_order_emails_list()
    if emails:
        return emails
    from django.conf import settings as django_settings
    return list(getattr(django_settings, "ORDER_EMAILS", []))


def get_webhook_url() -> str:
    settings = SiteSettings.load()
    if settings.webhook_url:
        return settings.webhook_url
    from django.conf import settings as django_settings
    return getattr(django_settings, "CRM_WEBHOOK_URL", "") or ""


def build_webhook_payload(quote: QuoteRequest) -> dict:
    return {
        "event": "quote.created",
        "quote_number": quote.number,
        "created_at": quote.created_at.isoformat(),
        "customer": {
            "name": quote.contact_name,
            "company": quote.company_name,
            "email": quote.email,
            "phone": quote.phone,
            "inn": quote.inn,
        },
        "items": [
            {
                "sku": item.sku_code,
                "name": item.product_name,
                "price": float(item.unit_price),
                "quantity": item.quantity,
                "total": float(item.line_total),
            }
            for item in quote.items.all()
        ],
        "subtotal": float(quote.subtotal),
        "comment": quote.comment,
        "utm": {
            "source": quote.utm_source,
            "medium": quote.utm_medium,
            "campaign": quote.utm_campaign,
        },
    }
