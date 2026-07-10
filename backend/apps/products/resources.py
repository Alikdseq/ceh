from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget

from .models import Category, ProductGroup, ProductSpec, ProductVariant


class CategoryResource(resources.ModelResource):
    parent_slug = fields.Field(
        column_name="parent_slug",
        attribute="parent",
        widget=ForeignKeyWidget(Category, field="slug"),
    )

    class Meta:
        model = Category
        import_id_fields = ("slug",)
        fields = (
            "slug", "name", "parent_slug", "description", "meta_title",
            "meta_description", "h1", "sort_order", "is_active",
        )
        export_order = fields


class ProductGroupResource(resources.ModelResource):
    category_slug = fields.Field(
        column_name="category_slug",
        attribute="category",
        widget=ForeignKeyWidget(Category, field="slug"),
    )

    class Meta:
        model = ProductGroup
        import_id_fields = ("slug",)
        fields = (
            "slug", "name", "category_slug", "short_description", "series_code",
            "product_type", "nominal_current_a", "nominal_voltage_v", "poles",
            "application_category", "honest_sign", "meta_title", "meta_description",
            "h1", "is_active", "is_featured", "sort_order",
        )
        export_order = fields


class ProductVariantResource(resources.ModelResource):
    group_slug = fields.Field(
        column_name="group_slug",
        attribute="group",
        widget=ForeignKeyWidget(ProductGroup, field="slug"),
    )

    class Meta:
        model = ProductVariant
        import_id_fields = ("sku_code",)
        fields = (
            "sku_code", "slug", "group_slug", "execution", "coil_type",
            "coil_voltage_v", "aux_contacts", "price", "price_valid_from",
            "weight_net_kg", "weight_gross_kg", "stock_status",
            "is_default", "is_active",
        )
        export_order = fields


class ProductSpecResource(resources.ModelResource):
    group_slug = fields.Field(
        column_name="group_slug",
        attribute="group",
        widget=ForeignKeyWidget(ProductGroup, field="slug"),
    )

    class Meta:
        model = ProductSpec
        import_id_fields = ("group_slug", "spec_key")
        fields = ("group_slug", "spec_key", "spec_value", "spec_unit", "filterable", "sort_order")
        export_order = fields
