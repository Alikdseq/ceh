import uuid

from django.db import models
class SiteSettings(models.Model):
    """Singleton — всегда pk=1."""
    company_name = models.CharField("Название", max_length=255, default='АО «Электроконтактор»')
    phone_main = models.CharField("Телефон", max_length=30, default="(8672) 53-33-44")
    phone_sales = models.CharField("Отдел сбыта", max_length=30, blank=True)
    email_main = models.EmailField("Email", default="info@ekontaktor.ru")
    order_emails = models.TextField(
        "Email для заявок (через запятую)",
        default="info@ekontaktor.ru,elkonreal@yandex.ru",
    )
    address = models.TextField("Адрес", default="362003, г. Владикавказ, ул. Кабардинская, 8")
    requisites = models.TextField("Реквизиты", blank=True)
    webhook_url = models.URLField("CRM Webhook URL", blank=True)
    yandex_metrika_id = models.CharField("Яндекс.Метрика", max_length=20, blank=True)
    ga4_id = models.CharField("GA4 ID", max_length=30, blank=True)

    class Meta:
        verbose_name = "Настройки сайта"

    def __str__(self):
        return "Настройки сайта"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    def get_order_emails_list(self):
        return [e.strip() for e in self.order_emails.split(",") if e.strip()]


class PriceListSection(models.Model):
    name = models.CharField("Раздел", max_length=255)
    sort_order = models.PositiveIntegerField("Порядок", default=0)
    is_active = models.BooleanField("Активен", default=True)

    class Meta:
        verbose_name = "Раздел прайс-листа"
        verbose_name_plural = "Разделы прайс-листа"
        ordering = ["sort_order", "name"]

    def __str__(self):
        return self.name


class PriceListItem(models.Model):
    section = models.ForeignKey(
        PriceListSection,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="Раздел",
    )
    name = models.CharField("Наименование", max_length=255)
    price = models.DecimalField("Цена, ₽", max_digits=12, decimal_places=2, default=0)
    nominal_current_a = models.PositiveIntegerField("Ном. ток, А", null=True, blank=True)
    product_type = models.CharField("Тип", max_length=20, blank=True)
    notes = models.CharField("Примечание", max_length=255, blank=True)
    sort_order = models.PositiveIntegerField("Порядок", default=0)
    is_active = models.BooleanField("Активен", default=True)

    class Meta:
        verbose_name = "Позиция прайс-листа"
        verbose_name_plural = "Позиции прайс-листа"
        ordering = ["section__sort_order", "sort_order", "name"]

    def __str__(self):
        return self.name


class Page(models.Model):
    title = models.CharField("Заголовок", max_length=255)
    slug = models.SlugField(unique=True)
    body = models.TextField("Содержимое (HTML)")
    meta_title = models.CharField(max_length=255, blank=True)
    meta_description = models.TextField(blank=True)
    h1 = models.CharField(max_length=255, blank=True)
    is_published = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Страница"
        verbose_name_plural = "Страницы"
        ordering = ["sort_order"]

    def __str__(self):
        return self.title


class NewsPost(models.Model):
    title = models.CharField("Заголовок", max_length=255)
    slug = models.SlugField(unique=True)
    excerpt = models.TextField("Анонс", blank=True)
    body = models.TextField("Текст")
    image = models.ImageField(upload_to="news/", blank=True, null=True)
    meta_title = models.CharField(max_length=255, blank=True)
    meta_description = models.TextField(blank=True)
    is_published = models.BooleanField(default=True)
    published_at = models.DateTimeField()
    newsletter_sent_at = models.DateTimeField(
        "Рассылка отправлена",
        null=True,
        blank=True,
        editable=False,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Новость"
        verbose_name_plural = "Новости"
        ordering = ["-published_at"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if self.pk and self.newsletter_sent_at is None:
            previous = (
                NewsPost.objects.filter(pk=self.pk)
                .values_list("newsletter_sent_at", flat=True)
                .first()
            )
            if previous:
                self.newsletter_sent_at = previous
        super().save(*args, **kwargs)


class FAQItem(models.Model):
    category = models.CharField("Категория", max_length=100, default="general")
    question = models.CharField("Вопрос", max_length=500)
    answer = models.TextField("Ответ")
    sort_order = models.PositiveIntegerField(default=0)
    is_published = models.BooleanField(default=True)

    class Meta:
        verbose_name = "FAQ"
        verbose_name_plural = "FAQ"
        ordering = ["sort_order"]

    def __str__(self):
        return self.question[:80]
