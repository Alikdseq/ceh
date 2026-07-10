import uuid

from django.db import models


class NewsletterSubscriber(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Ожидает подтверждения"
        ACTIVE = "active", "Активен"
        UNSUBSCRIBED = "unsubscribed", "Отписан"

    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255, blank=True)
    company = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    confirm_token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    unsubscribe_token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    source = models.CharField(max_length=50, default="website")
    marketing_accepted = models.BooleanField(default=False)
    marketing_accepted_at = models.DateTimeField(null=True, blank=True)
    privacy_policy_version = models.CharField(max_length=50, blank=True)
    ip = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Подписчик"
        verbose_name_plural = "Подписчики"

    def __str__(self):
        return self.email


class NewsletterCampaign(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Черновик"
        SCHEDULED = "scheduled", "Запланирована"
        SENDING = "sending", "Отправляется"
        SENT = "sent", "Отправлена"

    subject = models.CharField(max_length=255)
    body_html = models.TextField()
    body_text = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    scheduled_at = models.DateTimeField(null=True, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    sent_count = models.PositiveIntegerField(default=0)
    created_by = models.ForeignKey(
        "auth.User", null=True, blank=True, on_delete=models.SET_NULL,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Рассылка"
        verbose_name_plural = "Рассылки"

    def __str__(self):
        return self.subject


class NewsletterSendLog(models.Model):
    class Status(models.TextChoices):
        SENT = "sent", "Отправлено"
        FAILED = "failed", "Ошибка"
        BOUNCED = "bounced", "Отклонено"

    campaign = models.ForeignKey(NewsletterCampaign, on_delete=models.CASCADE, related_name="send_logs")
    subscriber = models.ForeignKey(NewsletterSubscriber, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=Status.choices)
    error_message = models.TextField(blank=True)
    sent_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Лог отправки"
        verbose_name_plural = "Логи отправки"
