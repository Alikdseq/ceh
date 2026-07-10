import csv
import io

from django.contrib import admin, messages
from unfold.admin import ModelAdmin

from .models import NewsletterCampaign, NewsletterSendLog, NewsletterSubscriber
from .tasks import send_campaign_preview, send_campaign_task


@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(ModelAdmin):
    list_display = ("email", "name", "status", "subscribed_at", "confirmed_at")
    list_filter = ("status",)
    search_fields = ("email", "name", "company")
    readonly_fields = ("confirm_token", "unsubscribe_token", "subscribed_at", "confirmed_at")
    actions = ["export_csv"]

    @admin.action(description="Экспорт CSV")
    def export_csv(self, request, queryset):
        buffer = io.StringIO()
        writer = csv.writer(buffer, delimiter=";")
        writer.writerow(["email", "name", "company", "status", "subscribed_at"])
        for s in queryset:
            writer.writerow([s.email, s.name, s.company, s.status, s.subscribed_at.isoformat()])
        from django.http import HttpResponse
        response = HttpResponse(buffer.getvalue(), content_type="text/csv; charset=utf-8")
        response["Content-Disposition"] = 'attachment; filename="subscribers.csv"'
        return response


@admin.register(NewsletterCampaign)
class NewsletterCampaignAdmin(ModelAdmin):
    list_display = ("subject", "status", "sent_count", "scheduled_at", "sent_at", "created_at")
    list_filter = ("status",)
    search_fields = ("subject",)
    readonly_fields = ("sent_count", "sent_at", "created_at")
    actions = ["send_campaign", "preview_campaign"]

    @admin.action(description="Отправить рассылку")
    def send_campaign(self, request, queryset):
        for campaign in queryset.filter(status__in=["draft", "scheduled"]):
            send_campaign_task.delay(campaign.pk)
        self.message_user(request, "Рассылка поставлена в очередь Celery.", messages.SUCCESS)

    @admin.action(description="Предпросмотр на email администратора")
    def preview_campaign(self, request, queryset):
        email = request.user.email
        if not email:
            self.message_user(request, "У пользователя нет email.", messages.ERROR)
            return
        for campaign in queryset[:1]:
            send_campaign_preview.delay(campaign.pk, email)
        self.message_user(request, f"Preview отправлен на {email}", messages.SUCCESS)


@admin.register(NewsletterSendLog)
class NewsletterSendLogAdmin(ModelAdmin):
    list_display = ("campaign", "subscriber", "status", "sent_at")
    list_filter = ("status",)
    readonly_fields = ("campaign", "subscriber", "status", "error_message", "sent_at")
