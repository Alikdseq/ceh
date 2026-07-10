from django.db import models


class ContactLead(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=30, blank=True)
    message = models.TextField()
    ip = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    privacy_accepted = models.BooleanField(default=False)
    privacy_accepted_at = models.DateTimeField(null=True, blank=True)
    privacy_policy_version = models.CharField(max_length=50, blank=True)
    is_processed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Обращение"
        verbose_name_plural = "Обращения"
        ordering = ["-created_at"]


class CallbackLead(models.Model):
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=30)
    preferred_time = models.CharField(max_length=100, blank=True)
    ip = models.GenericIPAddressField(null=True, blank=True)
    is_processed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Заказ звонка"
        verbose_name_plural = "Заказы звонка"
        ordering = ["-created_at"]


class DocumentRequestLead(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    company = models.CharField(max_length=255, blank=True)
    document = models.ForeignKey(
        "docs.Document", null=True, blank=True, on_delete=models.SET_NULL,
    )
    message = models.TextField(blank=True)
    is_processed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Запрос документа"
        verbose_name_plural = "Запросы документов"
        ordering = ["-created_at"]
