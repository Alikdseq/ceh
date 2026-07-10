from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils import timezone

from ..models import NewsletterSubscriber
from ..serializers import get_site_url


def subscribe_email(email: str, name: str = "", source: str = "website") -> NewsletterSubscriber:
    subscriber, created = NewsletterSubscriber.objects.get_or_create(
        email=email.lower().strip(),
        defaults={"name": name, "source": source},
    )
    if not created:
        if subscriber.status == NewsletterSubscriber.Status.UNSUBSCRIBED:
            subscriber.status = NewsletterSubscriber.Status.PENDING
            subscriber.name = name or subscriber.name
            subscriber.save(update_fields=["status", "name"])
        elif subscriber.status == NewsletterSubscriber.Status.ACTIVE:
            return subscriber

    confirm_url = f"{get_site_url()}/subscribe/confirm/{subscriber.confirm_token}"
    subject = "Подтвердите подписку на новости Электроконтактор"
    html = render_to_string("newsletter/confirm_email.html", {
        "subscriber": subscriber,
        "confirm_url": confirm_url,
    })
    msg = EmailMessage(subject=subject, body=html, to=[subscriber.email])
    msg.content_subtype = "html"
    msg.send(fail_silently=False)
    return subscriber


def confirm_subscriber(token) -> NewsletterSubscriber | None:
    subscriber = NewsletterSubscriber.objects.filter(confirm_token=token).first()
    if not subscriber:
        return None
    subscriber.status = NewsletterSubscriber.Status.ACTIVE
    subscriber.confirmed_at = timezone.now()
    subscriber.save(update_fields=["status", "confirmed_at"])
    return subscriber


def unsubscribe(token) -> NewsletterSubscriber | None:
    subscriber = NewsletterSubscriber.objects.filter(unsubscribe_token=token).first()
    if not subscriber:
        return None
    subscriber.status = NewsletterSubscriber.Status.UNSUBSCRIBED
    subscriber.save(update_fields=["status"])
    return subscriber


def render_campaign_email(campaign, subscriber) -> str:
    unsubscribe_url = f"{get_site_url()}/unsubscribe/{subscriber.unsubscribe_token}"
    return render_to_string("newsletter/campaign_email.html", {
        "campaign": campaign,
        "subscriber": subscriber,
        "unsubscribe_url": unsubscribe_url,
    })
