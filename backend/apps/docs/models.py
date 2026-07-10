import uuid
import os

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


def document_upload_path(instance, filename):
    ext = os.path.splitext(filename)[1].lower()
    return f"docs/{instance.uuid_filename}{ext}"


class Document(models.Model):
    class DocType(models.TextChoices):
        PASSPORT = "passport", "Паспорт"
        CERTIFICATE = "certificate", "Сертификат"
        DRAWING_DWG = "drawing_dwg", "Чертёж DWG"
        DRAWING_PDF = "drawing_pdf", "Чертёж PDF"
        CATALOG = "catalog", "Каталог"
        TU = "tu", "ТУ"

    name = models.CharField("Название", max_length=255)
    file = models.FileField("Файл", upload_to=document_upload_path)
    uuid_filename = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    mime_type = models.CharField("MIME", max_length=100, blank=True)
    file_size = models.PositiveIntegerField("Размер, байт", default=0)
    doc_type = models.CharField("Тип", max_length=20, choices=DocType.choices, default=DocType.PASSPORT)
    language = models.CharField("Язык", max_length=5, default="ru")
    is_public = models.BooleanField("Публичный", default=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Документ"
        verbose_name_plural = "Документы"
        ordering = ["-uploaded_at"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.file and not self.file_size:
            self.file_size = self.file.size
        if self.file and hasattr(self.file, "content_type"):
            self.mime_type = self.file.content_type or ""
        super().save(*args, **kwargs)

    def clean(self):
        super().clean()
        if self.file and hasattr(self.file, "content_type"):
            allowed = getattr(settings, "ALLOWED_UPLOAD_MIME_TYPES", [])
            mime = self.file.content_type or ""
            if allowed and mime and mime not in allowed:
                raise ValidationError(f"Недопустимый тип файла: {mime}")


class ProductDocument(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name="product_links")
    group = models.ForeignKey(
        "products.ProductGroup", null=True, blank=True,
        on_delete=models.CASCADE, related_name="documents",
    )
    variant = models.ForeignKey(
        "products.ProductVariant", null=True, blank=True,
        on_delete=models.CASCADE, related_name="documents",
    )
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Документ товара"
        verbose_name_plural = "Документы товаров"
        ordering = ["sort_order"]

    def __str__(self):
        target = self.variant or self.group
        return f"{self.document.name} → {target}"

    def clean(self):
        if not self.group and not self.variant:
            raise ValidationError("Укажите группу или вариант товара")
