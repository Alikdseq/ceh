from django.contrib import admin
from django.utils import timezone
from unfold.admin import ModelAdmin, TabularInline
from unfold.decorators import display

from .models import CaseStudy, DeliveryCity, FAQItem, NewsPost, Page, PriceListItem, PriceListSection, SiteSettings


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "is_published", "sort_order")
    prepopulated_fields = {"slug": ("title",)}


@admin.register(CaseStudy)
class CaseStudyAdmin(ModelAdmin):
    list_display = ("title", "industry", "is_published", "published_at")
    list_filter = ("is_published", "industry")
    prepopulated_fields = {"slug": ("title",)}
    filter_horizontal = ("products",)
    search_fields = ("title", "slug")


@admin.register(DeliveryCity)
class DeliveryCityAdmin(ModelAdmin):
    list_display = ("name", "slug", "region_name", "is_indexable", "priority")
    list_filter = ("is_indexable",)
    search_fields = ("name", "slug", "region_name")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(NewsPost)
class NewsPostAdmin(ModelAdmin):
    list_display = ("title", "published_at", "is_published", "newsletter_sent_at")
    list_filter = ("is_published",)
    search_fields = ("title", "slug", "excerpt")
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ("newsletter_sent_at", "created_at")
    fieldsets = (
        (
            "Новость",
            {
                "fields": ("title", "slug", "is_published", "published_at"),
                "description": "Заголовок и дата публикации на сайте.",
            },
        ),
        (
            "Текст",
            {
                "fields": ("excerpt", "body", "image"),
                "description": (
                    "Краткий анонс — в списке новостей. Полный текст — на странице новости. "
                    "После публикации письмо уйдёт подписчикам."
                ),
            },
        ),
        (
            "Поисковики (необязательно)",
            {
                "fields": ("meta_title", "meta_description"),
                "classes": ("collapse",),
            },
        ),
        (
            "Рассылка",
            {
                "fields": ("newsletter_sent_at", "created_at"),
                "classes": ("collapse",),
            },
        ),
    )

    def save_model(self, request, obj, form, change):
        if not obj.published_at:
            obj.published_at = timezone.now()
        super().save_model(request, obj, form, change)


@admin.register(FAQItem)
class FAQItemAdmin(admin.ModelAdmin):
    list_display = ("question", "category", "is_published", "sort_order")
    list_filter = ("category", "is_published")


class PriceListItemInline(TabularInline):
    model = PriceListItem
    extra = 1
    verbose_name = "Позиция"
    verbose_name_plural = "Позиции в разделе"
    fields = ("name", "price", "nominal_current_a", "notes", "sort_order", "is_active")
    ordering = ("sort_order", "name")

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        formfield = super().formfield_for_dbfield(db_field, request, **kwargs)
        labels = {
            "name": "Наименование",
            "price": "Цена, ₽",
            "nominal_current_a": "Ток, А",
            "notes": "Примечание",
            "sort_order": "Порядок",
            "is_active": "Показывать",
            "product_type": "Тип",
        }
        if db_field.name in labels:
            formfield.label = labels[db_field.name]
        return formfield


@admin.register(PriceListSection)
class PriceListSectionAdmin(ModelAdmin):
    list_display = ("name", "sort_order", "is_active", "item_count")
    list_editable = ("sort_order", "is_active")
    inlines = [PriceListItemInline]
    fieldsets = (
        (
            "Раздел прайс-листа",
            {
                "fields": ("name", "sort_order", "is_active"),
                "description": "Например: «Контакторы», «Аксессуары». Ниже — строки таблицы на странице «Прайс-лист».",
            },
        ),
    )

    @display(description="Позиций")
    def item_count(self, obj):
        return obj.items.filter(is_active=True).count()


@admin.register(PriceListItem)
class PriceListItemAdmin(ModelAdmin):
    list_display = ("name", "section", "price", "nominal_current_a", "sort_order", "is_active")
    list_filter = ("section", "is_active")
    search_fields = ("name", "notes")
    list_editable = ("sort_order", "is_active", "price")
    fieldsets = (
        (
            None,
            {
                "fields": ("section", "name", "price", "nominal_current_a", "notes", "sort_order", "is_active"),
            },
        ),
    )

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        formfield = super().formfield_for_dbfield(db_field, request, **kwargs)
        if db_field.name == "product_type":
            formfield.widget = formfield.hidden_widget()
        return formfield
