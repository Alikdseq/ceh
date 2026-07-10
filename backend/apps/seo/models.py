from django.db import models


class Redirect(models.Model):
    old_path = models.CharField(max_length=500, unique=True, db_index=True)
    new_path = models.CharField(max_length=500)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Редирект"
        verbose_name_plural = "Редиректы"

    def __str__(self):
        return f"{self.old_path} → {self.new_path}"


class SearchQueryLog(models.Model):
    query = models.CharField(max_length=255, db_index=True)
    results_count = models.PositiveIntegerField(default=0)
    ip = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Поисковый запрос"
        verbose_name_plural = "Поисковые запросы"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.query} ({self.results_count})"
