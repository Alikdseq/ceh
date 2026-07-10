import logging

import requests
from celery import shared_task
from django.core.mail import EmailMessage
from django.template.loader import render_to_string

from apps.quotes.services.quotes import get_order_recipients, get_webhook_url

from apps.leads.models import CallbackLead, ContactLead
from apps.leads.services.leads import build_lead_webhook_payload

logger = logging.getLogger(__name__)


@shared_task
def notify_contact_lead(lead_id: int) -> None:
    lead = ContactLead.objects.get(pk=lead_id)
    recipients = get_order_recipients()
    if not recipients:
        return
    subject = f"[Обращение] {lead.name} — {lead.email}"
    html = render_to_string("leads/email_contact.html", {"lead": lead})
    msg = EmailMessage(subject=subject, body=html, to=recipients)
    msg.content_subtype = "html"
    msg.send(fail_silently=False)


@shared_task
def notify_callback_lead(lead_id: int) -> None:
    lead = CallbackLead.objects.get(pk=lead_id)
    recipients = get_order_recipients()
    if not recipients:
        return
    subject = f"[Заказ звонка] {lead.name} — {lead.phone}"
    html = render_to_string("leads/email_callback.html", {"lead": lead})
    msg = EmailMessage(subject=subject, body=html, to=recipients)
    msg.content_subtype = "html"
    msg.send(fail_silently=False)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_lead_webhook(self, lead_type: str, lead_id: int) -> None:
    url = get_webhook_url()
    if not url:
        return
    if lead_type == "contact":
        lead = ContactLead.objects.get(pk=lead_id)
    else:
        lead = CallbackLead.objects.get(pk=lead_id)
    payload = build_lead_webhook_payload(lead_type, lead)
    try:
        response = requests.post(url, json=payload, timeout=15)
        response.raise_for_status()
        logger.info("Lead webhook sent: %s #%s", lead_type, lead_id)
    except requests.RequestException as exc:
        logger.warning("Lead webhook failed: %s", exc)
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))
