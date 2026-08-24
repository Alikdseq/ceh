from django.contrib import admin, messages
from django.core.exceptions import PermissionDenied
from django.db.models import Min
from django.shortcuts import get_object_or_404, redirect
from django.urls import path, reverse
from django.utils.html import escape, format_html
from django.utils.safestring import mark_safe
from django.utils.text import slugify
from mptt.admin import DraggableMPTTAdmin
from unfold.admin import ModelAdmin, StackedInline, TabularInline
from unfold.decorators import display

from .admin_forms import ProductGroupAdminForm, ProductSpecAdminForm, ProductVariantAdminForm
from .admin_helpers import ProductImageAdminForm, SafeClearableFileInput, safe_file_url
from .models import Category, ProductFAQ, ProductGroup, ProductImage, ProductSpec, ProductVariant, QuickCatalogCategory
from .product_media import prune_broken_images_for_group
from .utils import invalidate_catalog_cache


class ProductFAQInline(TabularInline):
    model = ProductFAQ
    extra = 0
    fields = ("question", "answer", "sort_order")
    ordering = ("sort_order",)


class ProductImageInline(StackedInline):
    model = ProductImage
    form = ProductImageAdminForm
    extra = 0
    min_num = 0
    can_delete = True
    verbose_name = "Фото"
    verbose_name_plural = "Фотографии товара"
    fields = ("image", "alt", "sort_order", "is_primary")
    classes = []
    ordering = ("sort_order",)

    def get_extra(self, request, obj=None, **kwargs):
        if obj is None:
            return 1
        return 0 if obj.images.exists() else 1

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        formfield = super().formfield_for_dbfield(db_field, request, **kwargs)
        if db_field.name == "image":
            formfield.widget = SafeClearableFileInput()
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
    extra = 0
    verbose_name = "Характеристика"
    verbose_name_plural = "Технические характеристики"
    fields = ("spec_key", "spec_value", "spec_unit", "filterable", "sort_order")
    ordering = ("sort_order", "spec_key")

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.exclude(spec_key__in=("nominal_current", "current"))

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        formset.form.base_fields["spec_key"].help_text = (
            "Номинальный ток — в блоке «Параметры для фильтров». "
            "Габариты: на сайте есть кнопка «Смотреть» к схеме gabariti.png."
        )
        return formset

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
                "description": "Картинка категории для быстрого каталога — удобнее редактировать в разделе «Быстрый каталог».",
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

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        formfield = super().formfield_for_dbfield(db_field, request, **kwargs)
        if db_field.name == "image":
            formfield.widget = SafeClearableFileInput()
        return formfield

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        invalidate_catalog_cache()

    def delete_model(self, request, obj):
        super().delete_model(request, obj)
        invalidate_catalog_cache()


@admin.register(QuickCatalogCategory)
class QuickCatalogCategoryAdmin(ModelAdmin):
    """Root catalog cards on the homepage — name, subtitle, and icon photo."""

    list_display = ("name", "card_image_preview", "sort_order", "is_active", "product_count")
    list_display_links = ("name",)
    list_editable = ("sort_order", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name", "slug", "description")
    ordering = ("sort_order", "name")
    readonly_fields = ("card_image_preview", "slug")
    list_per_page = 25

    fieldsets = (
        (
            "Карточка быстрого каталога",
            {
                "fields": (
                    "card_image_preview",
                    "name",
                    "description",
                    "image",
                    "sort_order",
                    "is_active",
                ),
                "description": (
                    "Эти карточки показываются на главной странице и в начале раздела «Каталог». "
                    "Загрузите квадратное фото (PNG/JPG) — оно заменит значок по умолчанию."
                ),
            },
        ),
        (
            "SEO и адрес",
            {
                "fields": ("slug", "h1", "meta_title", "meta_description"),
                "classes": ("collapse",),
            },
        ),
    )

    @display(description="Фото")
    def card_image_preview(self, obj):
        if not obj.pk:
            return "—"
        url = safe_file_url(obj.image)
        if url:
            return format_html(
                '<img src="{}" alt="" style="height:96px;width:96px;object-fit:contain;'
                'border:1px solid #dce4ec;border-radius:12px;background:#fff;padding:6px;" />',
                url,
            )
        return format_html('<span class="opacity-70">Значок по умолчанию (загрузите фото ниже)</span>')

    @display(description="Товаров")
    def product_count(self, obj):
        return obj.product_groups.filter(is_active=True).count()

    def get_queryset(self, request):
        return QuickCatalogCategory.objects.filter(parent__isnull=True)

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        formfield = super().formfield_for_dbfield(db_field, request, **kwargs)
        if db_field.name == "image":
            formfield.widget = SafeClearableFileInput()
            formfield.label = "Фото карточки"
            formfield.help_text = "Рекомендуется квадратное изображение на белом фоне, до 2 МБ."
        if db_field.name == "description":
            formfield.label = "Подзаголовок"
            formfield.help_text = "Короткая строка под названием, например «КТ 6000, 6600, 7200»."
        if db_field.name == "name":
            formfield.label = "Название на карточке"
        return formfield

    def save_model(self, request, obj, form, change):
        obj.parent = None
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
    inlines = [ProductImageInline, ProductVariantInline, ProductSpecInline, ProductFAQInline]
    readonly_fields = (
        "card_preview",
        "photos_preview",
        "image_rotation_controls",
        "dimensions_preview",
        "updated_at",
        "created_at",
    )
    list_per_page = 25
    warn_unsaved_form = False

    fieldsets = (
        (
            "Главное",
            {
                "fields": (
                    "card_preview",
                    "photos_preview",
                    "image_rotation_controls",
                    "dimensions_preview",
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
                "description": (
                    "Используются в каталоге и карточке. Тип и серия помогают группировать товары. "
                    "Номинальный ток — только здесь (не дублируйте в характеристиках). "
                    "«Честный знак» — только КТ/КТП, не КТЭ."
                ),
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
        url = safe_file_url(image.image) if image else None
        if url:
            return format_html(
                '<img src="{}" alt="" style="height:48px;width:auto;border-radius:6px;object-fit:contain;" />',
                url,
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

    @display(description="Габариты")
    def dimensions_preview(self, obj):
        if not obj.pk:
            return "—"
        spec = obj.specs.filter(spec_key="overall_dimensions").first()
        pdf_url = "/photos/gabariti-kontaktory.png"
        if not spec:
            return format_html(
                '<span class="opacity-70">—</span> · '
                '<a href="{}" target="_blank" rel="noopener">Схема габаритов (PNG)</a>',
                pdf_url,
            )
        return format_html(
            '{} · <a href="{}" target="_blank" rel="noopener">Смотреть схему (PNG)</a>',
            spec.spec_value,
            pdf_url,
        )

    @display(description="Фотографии")
    def photos_preview(self, obj):
        if not obj.pk:
            return "—"
        images = list(obj.images.all()[:12])
        if not images:
            return format_html('<p class="text-sm opacity-70">Нет загруженных фото</p>')
        parts = []
        for img in images:
            url = safe_file_url(img.image)
            if not url:
                continue
            parts.append(
                format_html(
                    '<figure style="display:inline-block;margin:4px;text-align:center;">'
                    '<img src="{}" alt="" style="height:72px;width:72px;object-fit:contain;border:1px solid #dce4ec;border-radius:8px;background:#fff;" />'
                    '<figcaption style="font-size:11px;max-width:72px;">{}</figcaption></figure>',
                    url,
                    "★" if img.is_primary else f"#{img.sort_order}",
                )
            )
        if not parts:
            return format_html(
                "<p class=\"text-sm opacity-70\">{}</p>",
                "Нет доступных файлов фото (запись в БД есть, файлы на диске отсутствуют)",
            )
        gallery = mark_safe("".join(str(fragment) for fragment in parts))
        return format_html(
            '<div><p class="text-sm mb-2">Всего: {} шт.</p><div>{}</div></div>',
            obj.images.count(),
            gallery,
        )

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
                <div>{}</div>
              </div>
              <div class="rounded-default border border-base-200 dark:border-base-700 p-3">
                <div class="font-semibold mb-1">Варианты и цены</div>
                <div>{} шт. · от {}</div>
              </div>
              <div class="rounded-default border border-base-200 dark:border-base-700 p-3">
                <div class="font-semibold mb-1">Фото</div>
                <div>{} шт.</div>
              </div>
              <div class="rounded-default border border-base-200 dark:border-base-700 p-3">
                <div class="font-semibold mb-1">Характеристики</div>
                <div>{} шт.</div>
              </div>
            </div>
            """,
            escape(f"{status}{featured}"),
            variants,
            escape(price),
            photos,
            specs,
        )

    def save_model(self, request, obj, form, change):
        if not obj.slug and obj.name:
            obj.slug = slugify(obj.name, allow_unicode=True)
        super().save_model(request, obj, form, change)
        invalidate_catalog_cache()

    def save_formset(self, request, form, formset, change):
        super().save_formset(request, form, formset, change)
        group = form.instance
        if formset.model == ProductSpec and group.pk and group.nominal_current_a:
            group.specs.filter(spec_key__in=("nominal_current", "current")).delete()
        if formset.model in (ProductSpec, ProductVariant, ProductImage):
            invalidate_catalog_cache()

    def delete_model(self, request, obj):
        super().delete_model(request, obj)
        invalidate_catalog_cache()

    def change_view(self, request, object_id, form_url="", extra_context=None):
        try:
            group = ProductGroup.objects.get(pk=object_id)
            removed = prune_broken_images_for_group(group)
            if removed:
                invalidate_catalog_cache()
            if group.nominal_current_a:
                deleted, _ = group.specs.filter(spec_key__in=("nominal_current", "current")).delete()
                if deleted:
                    invalidate_catalog_cache()
        except ProductGroup.DoesNotExist:
            pass
        return super().change_view(request, object_id, form_url, extra_context=extra_context)

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("category")
            .prefetch_related("variants")
        )

    def get_urls(self):
        urls = super().get_urls()
        custom = [
            path(
                "<int:object_id>/rotate-image/",
                self.admin_site.admin_view(self.rotate_image_view),
                name="products_productgroup_rotate_image",
            ),
        ]
        return custom + urls

    def rotate_image_view(self, request, object_id):
        obj = get_object_or_404(ProductGroup, pk=object_id)
        if not self.has_change_permission(request, obj):
            raise PermissionDenied
        direction = request.GET.get("dir")
        if direction == "cw":
            obj.image_rotation = (int(obj.image_rotation or 0) + 90) % 360
        elif direction == "ccw":
            obj.image_rotation = (int(obj.image_rotation or 0) - 90) % 360
        elif direction == "reset":
            obj.image_rotation = 0
        else:
            messages.error(request, "Неизвестное действие поворота.")
            return redirect(reverse("admin:products_productgroup_change", args=[object_id]))
        obj.save(update_fields=["image_rotation", "updated_at"])
        invalidate_catalog_cache()
        messages.success(request, f"Поворот фото на сайте: {obj.image_rotation}°")
        return redirect(reverse("admin:products_productgroup_change", args=[object_id]))

    @display(description="Поворот фото на сайте")
    def image_rotation_controls(self, obj):
        if not obj.pk:
            return format_html(
                '<p class="text-sm opacity-70">Сохраните карточку — появятся кнопки поворота для каталога и страницы товара.</p>'
            )
        rotate_url = reverse("admin:products_productgroup_rotate_image", args=[obj.pk])
        rotation = int(getattr(obj, "image_rotation", 0) or 0)
        primary = obj.images.filter(is_primary=True).first() or obj.images.first()
        preview_block = ""
        primary_url = safe_file_url(primary.image) if primary else None
        if primary_url:
            preview_block = format_html(
                '<img src="{}" alt="" style="height:120px;width:120px;object-fit:contain;'
                'border:1px solid #dce4ec;border-radius:8px;background:#fff;'
                'transform:rotate({}deg);margin-right:16px;" />',
                primary_url,
                rotation,
            )
        return format_html(
            '<div style="display:flex;align-items:center;flex-wrap:wrap;gap:12px;">'
            "{}"
            '<div style="display:flex;flex-direction:column;gap:8px;">'
            '<p style="margin:0;font-weight:600;">Текущий угол: {}°</p>'
            '<p style="margin:0;font-size:12px;opacity:0.75;">Действует для фото в каталоге и в карточке на сайте (в т.ч. статические снимки).</p>'
            '<div style="display:flex;flex-wrap:wrap;gap:8px;">'
            '<a class="button" href="{}?dir=ccw">↺ 90° против часовой</a>'
            '<a class="button" href="{}?dir=cw">↻ 90° по часовой</a>'
            '<a class="button" href="{}?dir=reset">Сброс (0°)</a>'
            "</div></div></div>",
            preview_block,
            rotation,
            rotate_url,
            rotate_url,
            rotate_url,
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
