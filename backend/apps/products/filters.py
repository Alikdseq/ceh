import django_filters
from django.db.models import Min, Q

from .models import ProductGroup, ProductVariant


class ProductGroupFilter(django_filters.FilterSet):
    current = django_filters.NumberFilter(field_name="nominal_current_a")
    poles = django_filters.NumberFilter(field_name="poles")
    product_type = django_filters.CharFilter(field_name="product_type")
    series_code = django_filters.CharFilter(field_name="series_code")
    category = django_filters.CharFilter(method="filter_category")
    featured = django_filters.BooleanFilter(field_name="is_featured")
    execution = django_filters.CharFilter(method="filter_execution")
    coil_voltage = django_filters.NumberFilter(method="filter_coil_voltage")

    class Meta:
        model = ProductGroup
        fields = ["current", "poles", "product_type", "series_code", "category", "featured", "execution", "coil_voltage"]

    def filter_category(self, queryset, name, value):
        from .models import Category

        cat = Category.objects.filter(slug=value, is_active=True).first()
        if not cat:
            return queryset.none()
        category_ids = cat.get_descendants(include_self=True).filter(is_active=True).values_list("id", flat=True)
        return queryset.filter(category_id__in=category_ids)

    def filter_execution(self, queryset, name, value):
        return queryset.filter(variants__execution=value, variants__is_active=True).distinct()

    def filter_coil_voltage(self, queryset, name, value):
        return queryset.filter(variants__coil_voltage_v=value, variants__is_active=True).distinct()


class ProductGroupOrderingFilter(django_filters.OrderingFilter):
    pass
