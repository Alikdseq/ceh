import logging
import time

from celery import shared_task
from django.core.mail import EmailMessage
from django.utils import timezone

from .models import NewsletterCampaign, NewsletterSendLog, NewsletterSubscriber
from .services.newsletter import render_campaign_email

logger = logging.getLogger(__name__)
BATCH_SIZE = 100
THROTTLE_SECONDS = 60


@shared_task
def send_campaign_task(campaign_id: int) -> None:
    campaign = NewsletterCampaign.objects.get(pk=campaign_id)
    if campaign.status not in (
        NewsletterCampaign.Status.DRAFT,
        NewsletterCampaign.Status.SCHEDULED,
    ):
        return

    campaign.status = NewsletterCampaign.Status.SENDING
    campaign.save(update_fields=["status"])

    subscribers = NewsletterSubscriber.objects.filter(status=NewsletterSubscriber.Status.ACTIVE)
    sent = 0
    batch_count = 0

    for subscriber in subscribers.iterator():
        try:
            html = render_campaign_email(campaign, subscriber)
            msg = EmailMessage(subject=campaign.subject, body=html, to=[subscriber.email])
            msg.content_subtype = "html"
            msg.send(fail_silently=False)
            NewsletterSendLog.objects.create(
                campaign=campaign,
                subscriber=subscriber,
                status=NewsletterSendLog.Status.SENT,
            )
            sent += 1
        except Exception as exc:
            NewsletterSendLog.objects.create(
                campaign=campaign,
                subscriber=subscriber,
                status=NewsletterSendLog.Status.FAILED,
                error_message=str(exc)[:500],
            )
            logger.exception("Campaign send failed for %s", subscriber.email)

        batch_count += 1
        if batch_count >= BATCH_SIZE:
            time.sleep(THROTTLE_SECONDS)
            batch_count = 0

    campaign.status = NewsletterCampaign.Status.SENT
    campaign.sent_at = timezone.now()
    campaign.sent_count = sent
    campaign.save(update_fields=["status", "sent_at", "sent_count"])
    logger.info("Campaign %s sent to %s subscribers", campaign.pk, sent)


@shared_task
def send_campaign_preview(campaign_id: int, test_email: str) -> None:
    campaign = NewsletterCampaign.objects.get(pk=campaign_id)
    fake = NewsletterSubscriber(email=test_email, name="Тест")
    html = render_campaign_email(campaign, fake)
    msg = EmailMessage(
        subject=f"[PREVIEW] {campaign.subject}",
        body=html,
        to=[test_email],
    )
    msg.content_subtype = "html"
    msg.send(fail_silently=False)
