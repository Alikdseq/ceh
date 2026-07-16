"""Safe file URL for Django admin previews (missing uploads must not 500)."""

from django import forms
from django.core.files.storage import default_storage
from django.forms.widgets import ClearableFileInput


def file_field_has_storage(file_field) -> bool:
    if not file_field or not file_field.name:
        return False
    try:
        return default_storage.exists(file_field.name)
    except OSError:
        return False


def safe_file_url(file_field) -> str | None:
    if not file_field:
        return None
    try:
        if not file_field.name:
            return None
        if not default_storage.exists(file_field.name):
            return None
        return file_field.url
    except (ValueError, OSError):
        return None


class SafeClearableFileInput(ClearableFileInput):
    """File widget that does not 500 when the stored path has no file on disk."""

    def get_context(self, name, value, attrs):
        try:
            return super().get_context(name, value, attrs)
        except ValueError:
            return super().get_context(name, None, attrs)

    def value_from_datadict(self, data, files, name):
        try:
            return super().value_from_datadict(data, files, name)
        except ValueError:
            return super().value_from_datadict(data, files, name)


class ProductImageAdminForm(forms.ModelForm):
    class Meta:
        from apps.products.models import ProductImage

        model = ProductImage
        fields = ("image", "alt", "sort_order", "is_primary")
        widgets = {"image": SafeClearableFileInput()}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk and self.instance.image and not file_field_has_storage(self.instance.image):
            self.initial["image"] = None
