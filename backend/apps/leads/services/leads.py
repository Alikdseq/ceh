import logging

from apps.content.models import SiteSettings
from apps.quotes.services.quotes import get_order_recipients, get_webhook_url
from django.utils import timezone

from ..models import CallbackLead, ContactLead

logger = logging.getLogger(__name__)


def _client_ip(request) -> str | None:
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


def create_contact_lead(data: dict, request) -> ContactLead:
    lead = ContactLead.objects.create(
        name=data["name"],
        email=data["email"],
        phone=data.get("phone", ""),
        message=data["message"],
        ip=_client_ip(request),
        user_agent=request.META.get("HTTP_USER_AGENT", "")[:500],
        privacy_accepted=bool(data.get("privacy_accepted")),
        privacy_accepted_at=timezone.now() if data.get("privacy_accepted") else None,
        privacy_policy_version=data.get("privacy_policy_version", "")[:50],
    )
    from ..tasks import notify_contact_lead, send_lead_webhook
    notify_contact_lead.delay(lead.pk)
    send_lead_webhook.delay("contact", lead.pk)
    return lead


def create_callback_lead(data: dict, request) -> CallbackLead:
    lead = CallbackLead.objects.create(
        name=data["name"],
        phone=data["phone"],
        preferred_time=data.get("preferred_time", ""),
        ip=_client_ip(request),
    )
    from ..tasks import notify_callback_lead, send_lead_webhook
    notify_callback_lead.delay(lead.pk)
    send_lead_webhook.delay("callback", lead.pk)
    return lead


def build_lead_webhook_payload(lead_type: str, lead) -> dict:
    if lead_type == "contact":
        return {
            "event": "lead.contact",
            "name": lead.name,
            "email": lead.email,
            "phone": lead.phone,
            "message": lead.message,
            "created_at": lead.created_at.isoformat(),
        }
    return {
        "event": "lead.callback",
        "name": lead.name,
        "phone": lead.phone,
        "preferred_time": lead.preferred_time,
        "created_at": lead.created_at.isoformat(),
    }
