from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline
from unfold.decorators import display

from .models import QuoteRequest, QuoteRequestItem


class QuoteRequestItemInline(TabularInline):
    model = QuoteRequestItem
    extra = 0
    can_delete = False
    verbose_name = "Позиция"
    verbose_name_plural = "Состав заявки"
    readonly_fields = ("sku_code", "product_name", "unit_price", "quantity", "line_total")

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        formfield = super().formfield_for_dbfield(db_field, request, **kwargs)
        labels = {
            "sku_code": "Артикул",
            "product_name": "Товар",
            "unit_price": "Цена",
            "quantity": "Кол-во",
            "line_total": "Сумма",
        }
        if db_field.name in labels:
            formfield.label = labels[db_field.name]
        return formfield


@admin.register(QuoteRequest)
class QuoteRequestAdmin(ModelAdmin):
    list_display = (
        "number",
        "company_name",
        "contact_name",
        "phone",
        "status_badge",
        "subtotal",
        "created_at",
    )
    list_filter = ("status", "created_at")
    search_fields = ("number", "company_name", "email", "contact_name", "phone", "inn")
    readonly_fields = (
        "number",
        "created_at",
        "subtotal",
        "contact_name",
        "company_name",
        "inn",
        "kpp",
        "email",
        "phone",
        "city",
        "comment",
        "vat_included",
        "ip",
        "user_agent",
        "utm_source",
        "utm_medium",
        "utm_campaign",
        "webhook_sent",
        "processed_at",
    )
    fieldsets = (
        (
            "Заявка",
            {
                "fields": (
                    "number",
                    "status",
                    "subtotal",
                    "vat_included",
                    "created_at",
                    "processed_at",
                ),
                "description": "Статус меняйте по мере работы с клиентом.",
            },
        ),
        (
            "Данные клиента",
            {
                "fields": (
                    "contact_name",
                    "company_name",
                    "inn",
                    "kpp",
                    "email",
                    "phone",
                    "city",
                    "comment",
                ),
            },
        ),
        (
            "Работа менеджера",
            {
                "fields": ("assigned_manager", "manager_comment"),
            },
        ),
    )
    inlines = [QuoteRequestItemInline]
    actions = ["mark_in_progress", "mark_quoted", "mark_completed"]

    @display(description="Статус", label=True)
    def status_badge(self, obj):
        return obj.get_status_display()

    @admin.action(description="Отметить «В работе»")
    def mark_in_progress(self, request, queryset):
        queryset.update(status=QuoteRequest.Status.IN_PROGRESS)

    @admin.action(description="Отметить «КП отправлено»")
    def mark_quoted(self, request, queryset):
        queryset.update(status=QuoteRequest.Status.QUOTED)

    @admin.action(description="Отметить «Завершена»")
    def mark_completed(self, request, queryset):
        queryset.update(status=QuoteRequest.Status.COMPLETED)
