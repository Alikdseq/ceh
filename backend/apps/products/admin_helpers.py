"""Safe file URL for Django admin previews (missing uploads must not 500)."""

from pathlib import Path

from django import forms
from django.forms.widgets import ClearableFileInput

from apps.products.catalog_static_photos import catalog_tovar_file
from apps.products.product_media import image_file_exists, safe_image_url


def file_field_has_storage(file_field) -> bool:
    return image_file_exists(file_field)


def safe_file_url(file_field, request=None) -> str | None:
    return safe_image_url(file_field, request)


def _image_has_display_source(file_field) -> bool:
    if not file_field or not getattr(file_field, "name", None):
        return False
    if image_file_exists(file_field):
        return True
    return catalog_tovar_file(Path(file_field.name).name) is not None


class SafeClearableFileInput(ClearableFileInput):
    """File widget that does not 500 when the stored path has no file on disk."""

    def is_initial(self, value):
        return _image_has_display_source(value)

    def get_context(self, name, value, attrs):
        if value and getattr(value, "name", None) and not image_file_exists(value):
            if not catalog_tovar_file(Path(value.name).name):
                value = None
        try:
            context = super().get_context(name, value, attrs)
        except ValueError:
            context = super().get_context(name, None, attrs)
        if value and getattr(value, "name", None):
            preview_url = safe_file_url(value)
            if preview_url:
                context["widget"]["is_initial"] = True
                context["widget"]["value"] = value
                context["widget"]["url"] = preview_url
        return context


class ProductImageAdminForm(forms.ModelForm):
    class Meta:
        from apps.products.models import ProductImage

        model = ProductImage
        fields = ("image", "alt", "sort_order", "is_primary")
        widgets = {"image": SafeClearableFileInput()}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["image"].required = False

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("DELETE"):
            return cleaned
        image = cleaned.get("image")
        if not self.instance.pk and not image:
            return cleaned
        if not image and not (self.instance.pk and self.instance.image):
            raise forms.ValidationError("Выберите файл изображения или удалите пустую строку.")
        return cleaned
