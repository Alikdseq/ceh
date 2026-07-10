from datetime import datetime
from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils import timezone


def generate_quote_number():
    year = timezone.now().year
    prefix = f"ЗК-{year}-"
    last = (
        QuoteRequest.objects.filter(number__startswith=prefix)
        .order_by("-number")
        .values_list("number", flat=True)
        .first()
    )
    if last:
        seq = int(last.split("-")[-1]) + 1
    else:
        seq = 1
    return f"{prefix}{seq:05d}"


class QuoteCart(models.Model):
    session_key = models.CharField(max_length=64, db_index=True, blank=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.CASCADE, related_name="quote_carts",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField()

    class Meta:
        verbose_name = "Корзина"
        verbose_name_plural = "Корзины"

    def __str__(self):
        return f"Cart {self.pk} ({self.session_key[:8]}…)"


class QuoteCartItem(models.Model):
    cart = models.ForeignKey(QuoteCart, on_delete=models.CASCADE, related_name="items")
    variant = models.ForeignKey("products.ProductVariant", on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    unit_price_snapshot = models.DecimalField(max_digits=12, decimal_places=2)
    coil_voltage_snapshot = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        verbose_name = "Позиция корзины"
        verbose_name_plural = "Позиции корзины"
        unique_together = [["cart", "variant"]]

    @property
    def line_total(self):
        return self.unit_price_snapshot * self.quantity


class QuoteRequest(models.Model):
    class Status(models.TextChoices):
        NEW = "new", "Новая"
        IN_PROGRESS = "in_progress", "В работе"
        QUOTED = "quoted", "КП отправлено"
        COMPLETED = "completed", "Завершена"
        CANCELLED = "cancelled", "Отменена"

    number = models.CharField("Номер", max_length=20, unique=True, editable=False)
    status = models.CharField("Статус", max_length=20, choices=Status.choices, default=Status.NEW)
    contact_name = models.CharField("ФИО", max_length=255)
    company_name = models.CharField("Компания", max_length=255)
    inn = models.CharField("ИНН", max_length=12, blank=True)
    kpp = models.CharField("КПП", max_length=9, blank=True)
    email = models.EmailField()
    phone = models.CharField("Телефон", max_length=30)
    city = models.CharField("Город", max_length=100, blank=True)
    comment = models.TextField("Комментарий", blank=True)
    subtotal = models.DecimalField("Итого", max_digits=14, decimal_places=2, default=Decimal("0"))
    vat_included = models.BooleanField("С НДС", default=True)
    ip = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    privacy_accepted = models.BooleanField("Согласие на ПДн", default=False)
    privacy_accepted_at = models.DateTimeField("Согласие на ПДн (время)", null=True, blank=True)
    privacy_policy_version = models.CharField("Версия политики ПДн", max_length=50, blank=True)
    utm_source = models.CharField(max_length=100, blank=True)
    utm_medium = models.CharField(max_length=100, blank=True)
    utm_campaign = models.CharField(max_length=100, blank=True)
    manager_comment = models.TextField("Комментарий менеджера", blank=True)
    assigned_manager = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, related_name="assigned_quotes",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    webhook_sent = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Заявка"
        verbose_name_plural = "Заявки"
        ordering = ["-created_at"]

    def __str__(self):
        return self.number

    def save(self, *args, **kwargs):
        if not self.number:
            self.number = generate_quote_number()
        super().save(*args, **kwargs)


class QuoteRequestItem(models.Model):
    request = models.ForeignKey(QuoteRequest, on_delete=models.CASCADE, related_name="items")
    sku_code = models.CharField("Артикул", max_length=100)
    product_name = models.CharField("Наименование", max_length=500)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    quantity = models.PositiveIntegerField()
    line_total = models.DecimalField(max_digits=14, decimal_places=2)

    class Meta:
        verbose_name = "Позиция заявки"
        verbose_name_plural = "Позиции заявки"

    def __str__(self):
        return f"{self.sku_code} × {self.quantity}"
