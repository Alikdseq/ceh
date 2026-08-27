"""Admin forms for content app."""

from django import forms
from unfold.widgets import UnfoldAdminTextInputWidget

from .models import PriceListItem


class PriceListItemAdminForm(forms.ModelForm):
    """Accept Russian decimal prices (12 345,67) and skip blank inline rows."""

    class Meta:
        model = PriceListItem
        fields = (
            "section",
            "name",
            "price",
            "nominal_current_a",
            "product_type",
            "notes",
            "sort_order",
            "is_active",
        )
        widgets = {
            "price": UnfoldAdminTextInputWidget(
                attrs={"inputmode": "decimal", "autocomplete": "off"},
            ),
        }
        labels = {
            "name": "Наименование",
            "price": "Цена, ₽",
            "nominal_current_a": "Ток, А",
            "notes": "Примечание",
            "sort_order": "Порядок",
            "is_active": "Показывать",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk:
            self.fields["name"].required = False

    def has_changed(self):
        if not self.instance.pk:
            prefix = self.add_prefix("name")
            raw = self.data.get(prefix, "") if self.data is not None else ""
            if not str(raw).strip():
                return False
        return super().has_changed()

    def full_clean(self):
        if hasattr(self.data, "copy"):
            data = self.data.copy()
            for field_name in ("price", "nominal_current_a"):
                key = self.add_prefix(field_name)
                raw = data.get(key)
                if isinstance(raw, str) and not raw.strip():
                    data[key] = ""
                elif isinstance(raw, str) and field_name == "price" and raw.strip():
                    data[key] = raw.strip().replace("\u00a0", "").replace(" ", "").replace(",", ".")
            self.data = data
        super().full_clean()

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("DELETE"):
            return cleaned
        name = (cleaned.get("name") or "").strip()
        if not self.instance.pk and not name:
            return cleaned
        if not name:
            self.add_error("name", "Укажите наименование.")
        else:
            cleaned["name"] = name
        return cleaned
