import pytest
from rest_framework.test import APIClient

from apps.leads.models import CallbackLead, ContactLead
from apps.newsletter.models import NewsletterSubscriber


@pytest.fixture
def api_client():
    return APIClient()


@pytest.mark.django_db
def test_contact_lead(api_client, settings):
    settings.CELERY_TASK_ALWAYS_EAGER = True
    settings.EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
    response = api_client.post(
        "/api/v1/leads/contact/",
        {
            "name": "Иван",
            "email": "ivan@test.ru",
            "phone": "+79991234567",
            "message": "Вопрос по каталогу",
            "website": "",
        },
        format="json",
    )
    assert response.status_code == 201
    assert ContactLead.objects.count() == 1


@pytest.mark.django_db
def test_callback_lead(api_client, settings):
    settings.CELERY_TASK_ALWAYS_EAGER = True
    settings.EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
    response = api_client.post(
        "/api/v1/leads/callback/",
        {"name": "Пётр", "phone": "+79991234567", "website": ""},
        format="json",
    )
    assert response.status_code == 201
    assert CallbackLead.objects.count() == 1


@pytest.mark.django_db
def test_newsletter_subscribe(api_client, settings):
    settings.EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
    response = api_client.post(
        "/api/v1/newsletter/subscribe/",
        {"email": "sub@test.ru", "name": "Test", "website": ""},
        format="json",
    )
    assert response.status_code == 201
    sub = NewsletterSubscriber.objects.get(email="sub@test.ru")
    assert sub.status == NewsletterSubscriber.Status.PENDING

    confirm = api_client.get(f"/api/v1/newsletter/confirm/{sub.confirm_token}/")
    assert confirm.status_code == 200
    sub.refresh_from_db()
    assert sub.status == NewsletterSubscriber.Status.ACTIVE

    unsub = api_client.get(f"/api/v1/newsletter/unsubscribe/{sub.unsubscribe_token}/")
    assert unsub.status_code == 200
    sub.refresh_from_db()
    assert sub.status == NewsletterSubscriber.Status.UNSUBSCRIBED
