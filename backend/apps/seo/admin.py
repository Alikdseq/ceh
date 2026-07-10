from django.contrib import admin

from .models import Redirect, SearchQueryLog


@admin.register(Redirect)
class RedirectAdmin(admin.ModelAdmin):
    list_display = ("old_path", "new_path", "is_active")
    search_fields = ("old_path", "new_path")


@admin.register(SearchQueryLog)
class SearchQueryLogAdmin(admin.ModelAdmin):
    list_display = ("query", "results_count", "created_at")
    list_filter = ("results_count",)
