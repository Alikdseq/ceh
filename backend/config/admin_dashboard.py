"""Главная страница админки — цифры и быстрые ссылки."""

from datetime import timedelta

from django.urls import reverse
from django.utils import timezone

from apps.content.models import NewsPost, PriceListItem
from apps.products.models import ProductGroup
from apps.quotes.models import QuoteRequest


def dashboard_callback(request, context):
    today = timezone.localdate()
    week_ago = today - timedelta(days=7)

    new_quotes = QuoteRequest.objects.filter(status=QuoteRequest.Status.NEW).count()
    quotes_week = QuoteRequest.objects.filter(created_at__date__gte=week_ago).count()
    active_products = ProductGroup.objects.filter(is_active=True).count()
    featured = ProductGroup.objects.filter(is_active=True, is_featured=True).count()
    news_live = NewsPost.objects.filter(is_published=True).count()
    pricelist_rows = PriceListItem.objects.filter(is_active=True).count()

    quotes_url = reverse("admin:quotes_quoterequest_changelist")
    products_url = reverse("admin:products_productgroup_changelist")
    pricelist_url = reverse("admin:content_pricelistsection_changelist")

    context["dashboard_stats"] = [
        {
            "title": "Новые заявки",
            "value": new_quotes,
            "hint": "Ждут ответа менеджера",
            "icon": "inbox",
            "link": f"{quotes_url}?status__exact=new",
            "accent": "red" if new_quotes else "default",
        },
        {
            "title": "Заявки за 7 дней",
            "value": quotes_week,
            "hint": "Всего поступило",
            "icon": "request_quote",
            "link": quotes_url,
            "accent": "default",
        },
        {
            "title": "Товары на сайте",
            "value": active_products,
            "hint": f"Из них хитов: {featured}",
            "icon": "inventory_2",
            "link": products_url,
            "accent": "default",
        },
        {
            "title": "Прайс-лист",
            "value": pricelist_rows,
            "hint": "Активных позиций",
            "icon": "payments",
            "link": pricelist_url,
            "accent": "default",
        },
    ]

    context["dashboard_quick_links"] = [
        {
            "title": "Добавить товар",
            "link": reverse("admin:products_productgroup_add"),
            "icon": "add_box",
        },
        {
            "title": "Категории каталога",
            "link": reverse("admin:products_category_changelist"),
            "icon": "category",
        },
        {
            "title": "Редактировать прайс",
            "link": pricelist_url,
            "icon": "table_chart",
        },
        {
            "title": "Новости",
            "link": reverse("admin:content_newspost_changelist"),
            "icon": "newspaper",
        },
    ]

    context["recent_quotes"] = [
        {
            "id": q.pk,
            "number": q.number,
            "company_name": q.company_name,
            "contact_name": q.contact_name,
            "status": q.get_status_display(),
            "subtotal": q.subtotal,
            "created_at": q.created_at,
            "url": reverse("admin:quotes_quoterequest_change", args=[q.pk]),
        }
        for q in QuoteRequest.objects.order_by("-created_at")[:5]
    ]

    context["dashboard_news_count"] = news_live
    return context
