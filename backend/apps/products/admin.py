from django.contrib import admin
from django.db.models import Min
from django.utils.html import format_html
from django.utils.text import slugify
from mptt.admin import DraggableMPTTAdmin
from unfold.admin import ModelAdmin, StackedInline, TabularInline
from unfold.decorators import display

from .admin_forms import ProductGroupAdminForm, ProductSpecAdminForm, ProductVariantAdminForm
from .models import Category, ProductGroup, ProductImage, ProductSpec, ProductVariant
from .utils import invalidate_catalog_cache


class ProductImageInline(StackedInline):
    model = ProductImage
    extra = 1
    verbose_name = "Фото"
    verbose_name_plural = "Фотографии товара"
    fields = ("image", "alt", "sort_order", "is_primary")
    classes = []
    ordering = ("sort_order",)

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        formfield = super().formfield_for_dbfield(db_field, request, **kwargs)
        if db_field.name == "alt":
            formfield.label = "Подпись к фото"
            formfield.help_text = "Кратко опишите, что на изображении."
        if db_field.name == "is_primary":
            formfield.label = "Главное фото"
            formfield.help_text = "Отображается в каталоге и вверху карточки."
        if db_field.name == "sort_order":
            formfield.label = "Порядок"
        return formfield


class ProductVariantInline(TabularInline):
    model = ProductVariant
    form = ProductVariantAdminForm
    extra = 0
    verbose_name = "Вариант"
    verbose_name_plural = "Варианты, цены и наличие"
    fields = (
        "sku_code",
        "execution",
        "coil_voltage_v",
        "aux_contacts",
        "price",
        "stock_status",
        "is_default",
        "is_active",
    )
    ordering = ("execution", "coil_voltage_v", "aux_contacts", "sku_code")
    show_change_link = False


class ProductSpecInline(TabularInline):
    model = ProductSpec
    form = ProductSpecAdminForm
    extra = 1
    verbose_name = "Характеристика"
    verbose_name_plural = "Технические характеристики"
    fields = ("spec_key", "spec_value", "spec_unit", "filterable", "sort_order")
    ordering = ("sort_order", "spec_key")

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        formfield = super().formfield_for_dbfield(db_field, request, **kwargs)
        return formfield


@admin.register(Category)
class CategoryAdmin(DraggableMPTTAdmin, ModelAdmin):
    list_display = ("tree_actions", "indented_title", "product_count", "is_active", "sort_order")
    list_display_links = ("indented_title",)
    list_filter = ("is_active",)
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name", "slug")
    mptt_level_indent = 20
    fieldsets = (
        (
            "Раздел каталога",
            {
                "fields": ("name", "parent", "is_active", "sort_order"),
                "description": "Как в меню «Каталог» на сайте: контакторы КТ, КТП и т.д.",
            },
        ),
        (
            "Описание и картинка",
            {
                "fields": ("description", "image"),
                "classes": ("collapse",),
            },
        ),
        (
            "Адрес страницы",
            {
                "fields": ("slug",),
                "description": "Заполняется из названия. Менять только если знаете, зачем.",
            },
        ),
    )

    @display(description="Товаров")
    def product_count(self, obj):
        return obj.product_groups.filter(is_active=True).count()

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        invalidate_catalog_cache()

    def delete_model(self, request, obj):
        super().delete_model(request, obj)
        invalidate_catalog_cache()


@admin.register(ProductGroup)
class ProductGroupAdmin(ModelAdmin):
    form = ProductGroupAdminForm
    list_display = (
        "name",
        "category",
        "thumbnail",
        "variants_count",
        "price_from_rub",
        "is_active",
        "is_featured",
        "updated_at",
    )
    list_display_links = ("name",)
    list_filter = ("category", "is_active", "is_featured", "product_type", "honest_sign")
    search_fields = ("name", "slug", "series_code", "variants__sku_code")
    prepopulated_fields = {"slug": ("name",)}
    autocomplete_fields = ("category",)
    filter_horizontal = ("related_groups",)
    inlines = [ProductImageInline, ProductVariantInline, ProductSpecInline]
    readonly_fields = ("card_preview", "updated_at", "created_at")
    list_per_page = 25
    warn_unsaved_form = True

    fieldsets = (
        (
            "Главное",
            {
                "fields": (
                    "card_preview",
                    "name",
                    "category",
                    "h1",
                    "is_active",
                    "is_featured",
                ),
                "description": (
                    "Название и категория — то, что видит посетитель в каталоге. "
                    "«Хит продаж» — блок на главной странице."
                ),
            },
        ),
        (
            "Текст на странице товара",
            {
                "fields": ("short_description", "full_description"),
            },
        ),
        (
            "Параметры для фильтров",
            {
                "fields": (
                    "product_type",
                    "series_code",
                    "nominal_current_a",
                    "nominal_voltage_v",
                    "poles",
                    "application_category",
                    "honest_sign",
                ),
                "description": "Используются в каталоге и карточке. Тип и серия помогают группировать товары.",
            },
        ),
        (
            "Связанные товары",
            {
                "fields": ("related_groups",),
                "classes": ("collapse",),
                "description": "Блок «Похожие товары» на странице.",
            },
        ),
        (
            "Настройки для поисковиков",
            {
                "fields": ("slug", "meta_title", "meta_description"),
                "classes": ("collapse",),
            },
        ),
        (
            "Служебное",
            {
                "fields": ("sort_order", "created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )

    add_fieldsets = (
        (
            "Новая карточка товара",
            {
                "fields": ("name", "category", "product_type", "series_code", "nominal_current_a", "is_active"),
                "description": "После сохранения добавьте фото, варианты с ценами и характеристики ниже.",
            },
        ),
    )

    @display(description="Фото")
    def thumbnail(self, obj):
        image = obj.images.filter(is_primary=True).first() or obj.images.first()
        if image and image.image:
            return format_html(
                '<img src="{}" alt="" style="height:48px;width:auto;border-radius:6px;object-fit:contain;" />',
                image.image.url,
            )
        return "—"

    @display(description="Вариантов")
    def variants_count(self, obj):
        return obj.variants.filter(is_active=True).count()

    @display(description="Цена от")
    def price_from_rub(self, obj):
        price = (
            obj.variants.filter(is_active=True, price__gt=0)
            .aggregate(min_price=Min("price"))
            .get("min_price")
        )
        if price:
            return f"{price:,.0f} ₽".replace(",", " ")
        return "по запросу"

    @display(description="Сводка")
    def card_preview(self, obj):
        if not obj.pk:
            return format_html(
                '<p class="text-sm opacity-70">После сохранения здесь появится краткая сводка по карточке.</p>'
            )
        variants = obj.variants.filter(is_active=True).count()
        specs = obj.specs.count()
        photos = obj.images.count()
        price = self.price_from_rub(obj)
        status = "На сайте" if obj.is_active else "Скрыт"
        featured = " · Хит продаж" if obj.is_featured else ""
        return format_html(
            """
            <div class="grid gap-3 sm:grid-cols-2 lg:grid-cols-4 text-sm">
              <div class="rounded-default border border-base-200 dark:border-base-700 p-3">
                <div class="font-semibold mb-1">Статус</div>
                <div>{status}{featured}</div>
              </div>
              <div class="rounded-default border border-base-200 dark:border-base-700 p-3">
                <div class="font-semibold mb-1">Варианты и цены</div>
                <div>{variants} шт. · от {price}</div>
              </div>
              <div class="rounded-default border border-base-200 dark:border-base-700 p-3">
                <div class="font-semibold mb-1">Фото</div>
                <div>{photos} шт.</div>
              </div>
              <div class="rounded-default border border-base-200 dark:border-base-700 p-3">
                <div class="font-semibold mb-1">Характеристики</div>
                <div>{specs} шт.</div>
              </div>
            </div>
            """,
            status=status,
            featured=featured,
            variants=variants,
            price=price,
            photos=photos,
            specs=specs,
        )

    def save_model(self, request, obj, form, change):
        if not obj.slug and obj.name:
            obj.slug = slugify(obj.name, allow_unicode=True)
        super().save_model(request, obj, form, change)
        invalidate_catalog_cache()

    def save_formset(self, request, form, formset, change):
        if formset.model is ProductVariant:
            instances = formset.save(commit=False)
            product_type = form.product_type
            for instance in instances:
                if product_type == "KTP":
                    instance.coil_type = ProductVariant.CoilType.DC
                elif product_type == "KT":
                    instance.coil_type = ProductVariant.CoilType.AC
                if not instance.slug and instance.sku_code:
                    from .admin_labels import auto_variant_slug

                    instance.slug = auto_variant_slug(instance.sku_code)
                instance.save()
            for obj in formset.deleted_objects:
                obj.delete()
            formset.save_m2m()
        else:
            super().save_formset(request, form, formset, change)
        if formset.model in (ProductSpec, ProductVariant, ProductImage):
            invalidate_catalog_cache()

    def delete_model(self, request, obj):
        super().delete_model(request, obj)
        invalidate_catalog_cache()

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("category")
            .prefetch_related("images", "variants")
        )


@admin.register(ProductVariant)
class ProductVariantAdmin(ModelAdmin):
    """Быстрое редактирование цен без входа в карточку товара."""

    form = ProductVariantAdminForm
    list_display = (
        "sku_code",
        "group",
        "execution",
        "coil_voltage_v",
        "aux_contacts",
        "price",
        "stock_status",
        "is_active",
    )
    list_display_links = ("sku_code",)
    list_editable = ("price", "stock_status", "is_active")
    list_filter = ("is_active", "stock_status", "group__category", "execution")
    search_fields = ("sku_code", "group__name", "group__slug")
    autocomplete_fields = ("group",)
    list_per_page = 50
    ordering = ("group__name", "sku_code")

    fieldsets = (
        (
            "Вариант",
            {
                "fields": (
                    "group",
                    "sku_code",
                    "slug",
                    "execution",
                    "coil_voltage_v",
                    "aux_contacts",
                    "price",
                    "price_valid_from",
                    "stock_status",
                    "is_default",
                    "is_active",
                ),
            },
        ),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("group", "group__category")

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        invalidate_catalog_cache()

    def changelist_view(self, request, extra_context=None):
        response = super().changelist_view(request, extra_context=extra_context)
        if request.method == "POST":
            invalidate_catalog_cache()
        return response
