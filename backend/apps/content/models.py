import uuid

from django.db import models
class SiteSettings(models.Model):
    """Singleton — всегда pk=1."""
    company_name = models.CharField("Название", max_length=255, default='АО «Электроконтактор»')
    phone_main = models.CharField("Телефон", max_length=30, default="(8672) 54-01-03")
    phone_sales = models.CharField("Отдел сбыта", max_length=80, blank=True)
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


class CaseStudy(models.Model):
    title = models.CharField("Заголовок", max_length=255)
    slug = models.SlugField(unique=True)
    excerpt = models.TextField("Анонс", blank=True)
    body = models.TextField("Текст (HTML)")
    industry = models.CharField("Отрасль", max_length=120, blank=True)
    meta_title = models.CharField(max_length=255, blank=True)
    meta_description = models.TextField(blank=True)
    image = models.ImageField(upload_to="cases/", blank=True, null=True)
    is_published = models.BooleanField(default=True)
    published_at = models.DateTimeField()
    products = models.ManyToManyField(
        "products.ProductGroup",
        blank=True,
        related_name="case_studies",
        verbose_name="Продукция",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Кейс / объект"
        verbose_name_plural = "Кейсы и объекты"
        ordering = ["-published_at"]

    def __str__(self):
        return self.title


class DeliveryCity(models.Model):
    slug = models.SlugField("URL", unique=True, max_length=80)
    name = models.CharField("Город", max_length=120)
    region_name = models.CharField("Регион", max_length=120, blank=True)
    priority = models.PositiveIntegerField("Приоритет", default=100, db_index=True)
    is_indexable = models.BooleanField(
        "Индексировать",
        default=False,
        help_text="True только при уникальном intro ≥ 400 символов",
    )
    intro_html = models.TextField("Уникальный текст", blank=True)
    meta_title = models.CharField(max_length=255, blank=True)
    meta_description = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Город доставки"
        verbose_name_plural = "Города доставки"
        ordering = ["priority", "name"]

    def __str__(self):
        return self.name

    @property
    def has_unique_intro(self) -> bool:
        from django.utils.html import strip_tags

        return len(strip_tags(self.intro_html or "").strip()) >= 400


class CityCategoryLanding(models.Model):
    city = models.ForeignKey(
        DeliveryCity,
        on_delete=models.CASCADE,
        related_name="category_landings",
    )
    category = models.ForeignKey(
        "products.Category",
        on_delete=models.CASCADE,
        related_name="city_landings",
    )
    intro_html = models.TextField("Уникальный текст", blank=True)
    is_indexable = models.BooleanField(default=False)
    meta_title = models.CharField(max_length=255, blank=True)
    meta_description = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Регион × категория"
        verbose_name_plural = "Региональные посадочные"
        constraints = [
            models.UniqueConstraint(fields=["city", "category"], name="uniq_city_category_landing"),
        ]

    def __str__(self):
        return f"{self.city.name} — {self.category.name}"
