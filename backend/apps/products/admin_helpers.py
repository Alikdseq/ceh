"""Safe file URL for Django admin previews (missing uploads must not 500)."""

from django import forms
from django.forms.widgets import ClearableFileInput

from apps.products.product_media import image_file_exists, safe_image_url


def file_field_has_storage(file_field) -> bool:
    return image_file_exists(file_field)


def safe_file_url(file_field) -> str | None:
    return safe_image_url(file_field)


class SafeClearableFileInput(ClearableFileInput):
    """File widget that does not 500 when the stored path has no file on disk."""

    def is_initial(self, value):
        if not value or not getattr(value, "name", None):
            return False
        if not image_file_exists(value):
            return False
        try:
            return bool(value.url)
        except (ValueError, OSError):
            return False

    def get_context(self, name, value, attrs):
        if value and getattr(value, "name", None) and not image_file_exists(value):
            value = None
        try:
            return super().get_context(name, value, attrs)
        except ValueError:
            return super().get_context(name, None, attrs)


class ProductImageAdminForm(forms.ModelForm):
    class Meta:
        from apps.products.models import ProductImage

        model = ProductImage
        fields = ("image", "alt", "sort_order", "is_primary")
        widgets = {"image": SafeClearableFileInput()}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk and self.instance.image and not image_file_exists(self.instance.image):
            self.initial["image"] = None
