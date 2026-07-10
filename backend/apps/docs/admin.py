from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from unfold.admin import ModelAdmin

from .models import Document, ProductDocument


@admin.register(Document)
class DocumentAdmin(ModelAdmin):
    list_display = ("name", "doc_type", "is_public", "file_size", "uploaded_at")
    list_filter = ("doc_type", "is_public")
    search_fields = ("name",)


@admin.register(ProductDocument)
class ProductDocumentAdmin(ModelAdmin):
    list_display = ("document", "group", "variant", "sort_order")
    list_filter = ("document__doc_type",)
    autocomplete_fields = ("document", "group", "variant")
