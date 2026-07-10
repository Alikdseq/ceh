from django.contrib import admin

from .models import CallbackLead, ContactLead, DocumentRequestLead


@admin.register(ContactLead)
class ContactLeadAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "is_processed", "created_at")
    list_filter = ("is_processed",)


@admin.register(CallbackLead)
class CallbackLeadAdmin(admin.ModelAdmin):
    list_display = ("name", "phone", "is_processed", "created_at")
    list_filter = ("is_processed",)


@admin.register(DocumentRequestLead)
class DocumentRequestLeadAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "document", "is_processed", "created_at")
