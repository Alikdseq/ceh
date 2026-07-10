import logging
import time

from celery import shared_task
from django.core.mail import EmailMessage
from django.db import transaction
from django.utils import timezone

from apps.content.models import NewsPost
from apps.content.services.newsletter import render_news_post_email
from apps.newsletter.models import NewsletterCampaign, NewsletterSendLog, NewsletterSubscriber

logger = logging.getLogger(__name__)
BATCH_SIZE = 100
THROTTLE_SECONDS = 60


@shared_task
def send_news_post_task(news_post_id: int) -> None:
    with transaction.atomic():
        news = (
            NewsPost.objects.select_for_update()
            .filter(pk=news_post_id, is_published=True, newsletter_sent_at__isnull=True)
            .first()
        )
        if not news:
            return
        NewsPost.objects.filter(pk=news.pk).update(newsletter_sent_at=timezone.now())
        news.refresh_from_db()

    subscribers = NewsletterSubscriber.objects.filter(status=NewsletterSubscriber.Status.ACTIVE)
    if not subscribers.exists():
        logger.info("News %s: no active subscribers, skipped email send", news.pk)
        return

    campaign = NewsletterCampaign.objects.create(
        subject=news.title,
        body_html=news.excerpt or news.body[:500],
        body_text=news.excerpt,
        status=NewsletterCampaign.Status.SENDING,
    )

    sent = 0
    batch_count = 0
    for subscriber in subscribers.iterator():
        try:
            html = render_news_post_email(news, subscriber)
            msg = EmailMessage(subject=news.title, body=html, to=[subscriber.email])
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
            logger.exception("News send failed for %s", subscriber.email)

        batch_count += 1
        if batch_count >= BATCH_SIZE:
            time.sleep(THROTTLE_SECONDS)
            batch_count = 0

    campaign.status = NewsletterCampaign.Status.SENT
    campaign.sent_at = timezone.now()
    campaign.sent_count = sent
    campaign.save(update_fields=["status", "sent_at", "sent_count"])
    logger.info("News %s emailed to %s subscribers", news.pk, sent)
