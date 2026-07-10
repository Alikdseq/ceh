from django import forms

from unfold.widgets import UnfoldAdminTextInputWidget, UnfoldAdminTextareaWidget

from .admin_labels import SPEC_KEY_CHOICES, auto_variant_slug, spec_label
from .models import ProductGroup, ProductSpec, ProductVariant


class ProductGroupAdminForm(forms.ModelForm):
    class Meta:
        model = ProductGroup
        fields = "__all__"
        widgets = {
            "short_description": UnfoldAdminTextareaWidget(attrs={"rows": 3}),
            "full_description": UnfoldAdminTextareaWidget(attrs={"rows": 8}),
            "name": UnfoldAdminTextInputWidget(attrs={"placeholder": "Контактор КТ 6012 100А"}),
            "h1": UnfoldAdminTextInputWidget(
                attrs={"placeholder": "Как показывать заголовок на странице товара"},
            ),
        }
        labels = {
            "h1": "Заголовок на странице",
            "product_type": "Тип продукции",
            "poles": "Число полюсов",
            "application_category": "Категория применения (AC-3, AC-4…)",
            "nominal_current_a": "Номинальный ток, А",
            "nominal_voltage_v": "Номинальное напряжение, В",
            "short_description": "Краткое описание",
            "full_description": "Полное описание",
            "category": "Раздел каталога",
            "name": "Название товара",
            "is_active": "Показывать на сайте",
            "is_featured": "Хит продаж (главная страница)",
            "related_groups": "Похожие товары",
            "sort_order": "Порядок в списке",
            "slug": "Адрес страницы",
            "meta_title": "Заголовок для поисковиков",
            "meta_description": "Описание для поисковиков",
        }
        help_texts = {
            "slug": "Адрес страницы латиницей. Обычно заполняется автоматически из названия.",
            "series_code": "Четыре цифры серии, например 6012.",
            "nominal_current_a": "Номинальный ток в амперах, например 100.",
            "nominal_voltage_v": "Напряжение силовой цепи, обычно 380 В.",
            "is_featured": "Показывать в блоке «Хиты продаж» на главной.",
            "is_active": "Снять галочку, чтобы скрыть товар с сайта без удаления.",
            "honest_sign": "Отметьте, если товар участвует в маркировке «Честный знак».",
            "meta_title": "Заголовок вкладки браузера и поисковиков (необязательно).",
            "meta_description": "Краткое описание для Google и Яндекса (необязательно).",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "slug" in self.fields and not self.instance.pk:
            self.fields["slug"].required = False


class ProductSpecAdminForm(forms.ModelForm):
    spec_key = forms.ChoiceField(
        label="Параметр",
        choices=[("", "— выберите —"), *SPEC_KEY_CHOICES],
    )

    class Meta:
        model = ProductSpec
        fields = ("spec_key", "spec_value", "spec_unit", "filterable", "sort_order")
        labels = {
            "spec_value": "Значение",
            "spec_unit": "Единица",
            "filterable": "Показывать в фильтре каталога",
            "sort_order": "Порядок",
        }
        widgets = {
            "spec_value": UnfoldAdminTextInputWidget(attrs={"placeholder": "100"}),
            "spec_unit": UnfoldAdminTextInputWidget(attrs={"placeholder": "А, В, Гц…"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        choices = list(SPEC_KEY_CHOICES)
        if self.instance.pk and self.instance.spec_key:
            key = self.instance.spec_key
            if key not in dict(choices):
                choices.insert(0, (key, spec_label(key)))
        self.fields["spec_key"].choices = [("", "— выберите —"), *choices]


class ProductVariantAdminForm(forms.ModelForm):
    class Meta:
        model = ProductVariant
        fields = (
            "sku_code",
            "execution",
            "coil_voltage_v",
            "aux_contacts",
            "price",
            "stock_status",
            "is_default",
            "is_active",
        )
        labels = {
            "sku_code": "Артикул",
            "execution": "Исполнение",
            "coil_voltage_v": "Катушка, В",
            "aux_contacts": "Всп. контакты",
            "price": "Цена, ₽",
            "stock_status": "Наличие",
            "is_default": "По умолчанию на сайте",
            "is_active": "Показывать",
        }
        help_texts = {
            "sku_code": "Из прайс-листа, например КТ6012Б-У3-220V",
            "aux_contacts": "2З+2Р или 3З+3Р",
            "is_default": "Какой вариант открывается первым в карточке.",
        }

    def save(self, commit=True):
        instance = super().save(commit=False)
        if not instance.slug:
            instance.slug = auto_variant_slug(instance.sku_code)
        if commit:
            instance.save()
            self.save_m2m()
        return instance
