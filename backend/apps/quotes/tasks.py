import logging
import time

import requests
from celery import shared_task
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils import timezone

from apps.content.models import SiteSettings

from .models import QuoteRequest
from .services.exports import render_quote_pdf
from .services.quotes import build_webhook_payload, get_order_recipients, get_webhook_url

logger = logging.getLogger(__name__)


@shared_task
def process_new_quote(quote_id: int) -> None:
    send_quote_notification.delay(quote_id)
    send_quote_confirmation.delay(quote_id)
    send_crm_webhook.delay(quote_id)


@shared_task
def send_quote_notification(quote_id: int) -> None:
    quote = QuoteRequest.objects.prefetch_related("items").get(pk=quote_id)
    recipients = get_order_recipients()
    if not recipients:
        logger.warning("No order email recipients configured")
        return

    subject = f"[Заявка {quote.number}] Запрос КП — {quote.company_name}"
    html = render_to_string("quotes/email_manager.html", {"quote": quote})
    msg = EmailMessage(subject=subject, body=html, to=recipients)
    msg.content_subtype = "html"
    msg.send(fail_silently=False)
    logger.info("Manager notification sent for %s", quote.number)


@shared_task
def send_quote_confirmation(quote_id: int) -> None:
    quote = QuoteRequest.objects.prefetch_related("items").get(pk=quote_id)
    settings = SiteSettings.load()

    subject = f"Ваша заявка принята № {quote.number}"
    html = render_to_string("quotes/email_client.html", {"quote": quote, "settings": settings})
    msg = EmailMessage(subject=subject, body=html, to=[quote.email])
    msg.content_subtype = "html"

    try:
        pdf_bytes = render_quote_pdf(quote)
        msg.attach(f"KP-{quote.number}.pdf", pdf_bytes, "application/pdf")
    except Exception:
        logger.exception("PDF generation failed for quote %s", quote.number)

    msg.send(fail_silently=False)
    logger.info("Client confirmation sent for %s", quote.number)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_crm_webhook(self, quote_id: int) -> None:
    quote = QuoteRequest.objects.prefetch_related("items").get(pk=quote_id)
    url = get_webhook_url()
    if not url:
        logger.info("CRM webhook URL not configured, skipping quote %s", quote.number)
        return

    payload = build_webhook_payload(quote)
    try:
        response = requests.post(url, json=payload, timeout=15)
        response.raise_for_status()
        quote.webhook_sent = True
        quote.save(update_fields=["webhook_sent"])
        logger.info("CRM webhook sent for %s", quote.number)
    except requests.RequestException as exc:
        logger.warning("CRM webhook failed for %s: %s", quote.number, exc)
        countdown = 60 * (2 ** self.request.retries)
        raise self.retry(exc=exc, countdown=countdown)
