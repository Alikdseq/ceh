from datetime import timedelta

import pytest
from django.core import mail
from django.utils import timezone

from apps.content.models import NewsPost
from apps.newsletter.models import NewsletterCampaign, NewsletterSendLog, NewsletterSubscriber


@pytest.mark.django_db
def test_published_news_sends_to_active_subscribers(settings):
    settings.CELERY_TASK_ALWAYS_EAGER = True
    settings.EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

    NewsletterSubscriber.objects.create(
        email="subscriber@example.com",
        status=NewsletterSubscriber.Status.ACTIVE,
        confirmed_at=timezone.now(),
    )
    NewsletterSubscriber.objects.create(
        email="pending@example.com",
        status=NewsletterSubscriber.Status.PENDING,
    )

    NewsPost.objects.create(
        title="Запуск новой серии",
        slug="new-series",
        excerpt="Краткий анонс",
        body="Полный текст новости.",
        is_published=True,
        published_at=timezone.now(),
    )

    assert len(mail.outbox) == 1
    assert mail.outbox[0].to == ["subscriber@example.com"]
    assert "Запуск новой серии" in mail.outbox[0].subject
    assert "/news/new-series/" in mail.outbox[0].body

    news = NewsPost.objects.get(slug="new-series")
    assert news.newsletter_sent_at is not None
    assert NewsletterCampaign.objects.count() == 1
    assert NewsletterSendLog.objects.filter(status=NewsletterSendLog.Status.SENT).count() == 1


@pytest.mark.django_db
def test_draft_news_does_not_send(settings):
    settings.CELERY_TASK_ALWAYS_EAGER = True
    settings.EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

    NewsletterSubscriber.objects.create(
        email="subscriber@example.com",
        status=NewsletterSubscriber.Status.ACTIVE,
        confirmed_at=timezone.now(),
    )

    NewsPost.objects.create(
        title="Черновик",
        slug="draft",
        body="Текст",
        is_published=False,
        published_at=timezone.now(),
    )

    assert len(mail.outbox) == 0


@pytest.mark.django_db
def test_published_news_not_sent_twice(settings):
    settings.CELERY_TASK_ALWAYS_EAGER = True
    settings.EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

    NewsletterSubscriber.objects.create(
        email="subscriber@example.com",
        status=NewsletterSubscriber.Status.ACTIVE,
        confirmed_at=timezone.now(),
    )

    news = NewsPost.objects.create(
        title="Одна рассылка",
        slug="once",
        body="Текст",
        is_published=True,
        published_at=timezone.now(),
    )
    assert len(mail.outbox) == 1

    news.title = "Обновлённый заголовок"
    news.save()
    assert len(mail.outbox) == 1


@pytest.mark.django_db
def test_news_sends_when_published_later(settings):
    settings.CELERY_TASK_ALWAYS_EAGER = True
    settings.EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

    NewsletterSubscriber.objects.create(
        email="subscriber@example.com",
        status=NewsletterSubscriber.Status.ACTIVE,
        confirmed_at=timezone.now(),
    )

    news = NewsPost.objects.create(
        title="Сначала черновик",
        slug="later",
        body="Текст",
        is_published=False,
        published_at=timezone.now() - timedelta(days=1),
    )
    assert len(mail.outbox) == 0

    news.is_published = True
    news.save()
    assert len(mail.outbox) == 1
