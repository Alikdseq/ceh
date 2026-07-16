from django.db import models
from django.utils.text import slugify
from mptt.models import MPTTModel, TreeForeignKey


class Category(MPTTModel):
    name = models.CharField("Название", max_length=255)
    slug = models.SlugField("Адрес страницы", max_length=255, unique=True)
    parent = TreeForeignKey(
        "self", null=True, blank=True, related_name="children",
        on_delete=models.CASCADE, verbose_name="Родитель",
    )
    description = models.TextField("Описание", blank=True)
    image = models.ImageField("Изображение", upload_to="categories/", blank=True, null=True)
    meta_title = models.CharField("Заголовок для поисковиков", max_length=255, blank=True)
    meta_description = models.TextField("Описание для поисковиков", blank=True)
    h1 = models.CharField("Заголовок на странице", max_length=255, blank=True)
    sort_order = models.PositiveIntegerField("Порядок", default=0)
    is_active = models.BooleanField("Активна", default=True)
    noindex = models.BooleanField("Noindex", default=False)
    canonical_override = models.CharField("Canonical URL", max_length=500, blank=True)

    class MPTTMeta:
        order_insertion_by = ["sort_order", "name"]

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ["sort_order", "name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)


class ProductGroup(models.Model):
    class ProductType(models.TextChoices):
        KT = "KT", "КТ (переменный ток)"
        KTP = "KTP", "КТП (постоянный ток)"
        KTE = "KTE", "КТЭ (электротранспорт)"
        ACCESSORY = "ACCESSORY", "Аксессуар"
        SWITCH = "SWITCH", "Выключатель"
        CAM = "CAM", "Кулачковый элемент"
        OTHER = "OTHER", "Прочее"

    category = models.ForeignKey(
        Category, on_delete=models.PROTECT, related_name="product_groups",
        verbose_name="Категория",
    )
    name = models.CharField("Название", max_length=255)
    slug = models.SlugField("Адрес страницы", max_length=255, unique=True)
    short_description = models.TextField("Краткое описание", blank=True)
    full_description = models.TextField("Полное описание", blank=True)
    series_code = models.CharField("Код серии", max_length=20, blank=True, db_index=True)
    product_type = models.CharField(
        "Тип", max_length=20, choices=ProductType.choices,
        default=ProductType.KT, db_index=True,
    )
    nominal_current_a = models.PositiveIntegerField("Ном. ток, А", null=True, blank=True, db_index=True)
    nominal_voltage_v = models.PositiveIntegerField("Ном. напряжение, В", default=380)
    poles = models.PositiveSmallIntegerField("Полюса", null=True, blank=True)
    application_category = models.CharField("Категория применения", max_length=50, blank=True)
    designation_structure = models.TextField("Структура обозначения (HTML)", blank=True)
    honest_sign = models.BooleanField("Честный знак", default=False)
    meta_title = models.CharField("Заголовок для поисковиков", max_length=255, blank=True)
    meta_description = models.TextField("Описание для поисковиков", blank=True)
    h1 = models.CharField("Заголовок на странице", max_length=255, blank=True)
    is_active = models.BooleanField("Активен", default=True, db_index=True)
    is_featured = models.BooleanField("Хит продаж", default=False)
    sort_order = models.PositiveIntegerField("Порядок", default=0)
    image_rotation = models.PositiveSmallIntegerField(
        "Поворот фото (градусы)",
        default=0,
        help_text="Отображение на сайте: 0, 90, 180 или 270. Настраивается кнопками в админке.",
    )
    search_vector = models.TextField("Search index", blank=True, editable=False)
    related_groups = models.ManyToManyField(
        "self", blank=True, symmetrical=False,
        related_name="related_to", verbose_name="Связанные товары",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Карточка товара"
        verbose_name_plural = "Карточки товаров"
        ordering = ["sort_order", "name"]
        indexes = [
            models.Index(fields=["category", "is_active"]),
            models.Index(fields=["nominal_current_a", "is_active"]),
        ]

    def __str__(self):
        return self.name

    @property
    def price_from(self):
        return self.variants.filter(is_active=True).order_by("price").values_list("price", flat=True).first()


class ProductVariant(models.Model):
    class Execution(models.TextChoices):
        B = "B", "Б"
        BS = "BS", "БС"
        S = "S", "С"
        NONE = "NONE", "—"

    class CoilType(models.TextChoices):
        AC = "AC", "Переменный"
        DC = "DC", "Постоянный"
        NONE = "NONE", "—"

    class StockStatus(models.TextChoices):
        IN_STOCK = "in_stock", "В наличии"
        ON_ORDER = "on_order", "Под заказ"
        DISCONTINUED = "discontinued", "Снят с производства"

    group = models.ForeignKey(
        ProductGroup, on_delete=models.CASCADE, related_name="variants",
        verbose_name="Карточка товара",
    )
    sku_code = models.CharField("Артикул", max_length=100, unique=True, db_index=True)
    slug = models.SlugField("Адрес варианта", max_length=150, unique=True)
    execution = models.CharField(
        "Исполнение", max_length=10, choices=Execution.choices,
        default=Execution.NONE, db_index=True,
    )
    coil_type = models.CharField(
        "Тип катушки", max_length=10, choices=CoilType.choices,
        default=CoilType.NONE,
    )
    coil_voltage_v = models.PositiveIntegerField("Напряжение катушки, В", null=True, blank=True, db_index=True)
    aux_contacts = models.CharField("Всп. контакты", max_length=50, blank=True)
    price = models.DecimalField("Цена, ₽", max_digits=12, decimal_places=2, default=0)
    price_valid_from = models.DateField("Цена действует с", null=True, blank=True)
    weight_net_kg = models.DecimalField("Вес нетто, кг", max_digits=8, decimal_places=2, null=True, blank=True)
    weight_gross_kg = models.DecimalField("Вес брутто, кг", max_digits=8, decimal_places=2, null=True, blank=True)
    dimensions = models.JSONField("Габариты", default=dict, blank=True)
    stock_status = models.CharField(
        "Наличие", max_length=20, choices=StockStatus.choices,
        default=StockStatus.IN_STOCK,
    )
    is_default = models.BooleanField("Вариант по умолчанию", default=False)
    is_active = models.BooleanField("Активен", default=True)
    search_vector = models.TextField("Search index", blank=True, editable=False)

    class Meta:
        verbose_name = "Вариант (цена и исполнение)"
        verbose_name_plural = "Варианты и цены"
        ordering = ["group", "sku_code"]
        indexes = [
            models.Index(fields=["execution", "coil_voltage_v"]),
        ]

    def __str__(self):
        return self.sku_code

    def save(self, *args, **kwargs):
        if self.group_id:
            product_type = self.group.product_type
            if product_type == ProductGroup.ProductType.KTP:
                self.coil_type = self.CoilType.DC
            elif product_type == ProductGroup.ProductType.KT:
                self.coil_type = self.CoilType.AC
        if not self.slug and self.sku_code:
            from apps.products.admin_labels import auto_variant_slug

            self.slug = auto_variant_slug(self.sku_code)
        super().save(*args, **kwargs)


class ProductSpec(models.Model):
    group = models.ForeignKey(
        ProductGroup, on_delete=models.CASCADE, related_name="specs",
        verbose_name="Карточка товара",
    )
    spec_key = models.SlugField("Параметр", max_length=100)
    spec_value = models.CharField("Значение", max_length=255)
    spec_unit = models.CharField("Единица", max_length=20, blank=True)
    filterable = models.BooleanField("В фильтре", default=False)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Характеристика"
        verbose_name_plural = "Характеристики"
        ordering = ["sort_order", "spec_key"]
        unique_together = [["group", "spec_key"]]

    def __str__(self):
        return f"{self.spec_key}: {self.spec_value}{self.spec_unit}"


class ProductImage(models.Model):
    group = models.ForeignKey(
        ProductGroup, on_delete=models.CASCADE, related_name="images",
        verbose_name="Карточка товара",
    )
    image = models.ImageField("Изображение", upload_to="products/")
    alt = models.CharField("Подпись к фото", max_length=255, blank=True)
    sort_order = models.PositiveIntegerField(default=0)
    is_primary = models.BooleanField("Основное", default=False)

    class Meta:
        verbose_name = "Изображение"
        verbose_name_plural = "Изображения"
        ordering = ["sort_order"]

    def __str__(self):
        return f"Image #{self.pk} — {self.group.name}"
