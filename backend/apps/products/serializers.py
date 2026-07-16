from django.db import models
from rest_framework import serializers

from apps.docs.models import Document, ProductDocument

from apps.core.media_urls import public_media_url

from .models import Category, ProductGroup, ProductImage, ProductSpec, ProductVariant
from .utils import category_path_slugs, get_public_category_ids, is_category_public, PUBLIC_HIDDEN_SPEC_KEYS


def _absolute_media_url(obj, request):
    from apps.products.product_media import safe_image_url

    if not obj:
        return None
    if hasattr(obj, "storage"):
        return safe_image_url(obj, request)
    return public_media_url(str(obj), request)


class CategoryTreeSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()
    product_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = (
            "id", "name", "slug", "description", "meta_title", "meta_description",
            "h1", "noindex", "canonical_override", "sort_order", "children", "product_count",
        )

    def get_children(self, obj):
        children = obj.get_children().filter(is_active=True)
        children = [child for child in children if is_category_public(child)]
        return CategoryTreeSerializer(children, many=True, context=self.context).data

    def get_product_count(self, obj):
        public_ids = get_public_category_ids()
        return ProductGroup.objects.filter(
            category_id__in=public_ids,
            category__tree_id=obj.tree_id,
            is_active=True,
        ).count()


class CategoryListSerializer(serializers.ModelSerializer):
    product_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ("id", "name", "slug", "sort_order", "product_count")

    def get_product_count(self, obj):
        return obj.product_groups.filter(is_active=True).count()


class ProductImageSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = ProductImage
        fields = ("id", "image", "url", "alt", "sort_order", "is_primary")

    def get_url(self, obj):
        return _absolute_media_url(obj.image, self.context.get("request"))


class ProductSpecSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductSpec
        fields = ("spec_key", "spec_value", "spec_unit", "filterable", "sort_order")


class DocumentBriefSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = Document
        fields = ("id", "name", "doc_type", "file_url", "file_size", "is_public")

    def get_file_url(self, obj):
        request = self.context.get("request")
        if obj.file:
            return public_media_url(obj.file.url, request)
        return None


class ProductDocumentSerializer(serializers.ModelSerializer):
    document = DocumentBriefSerializer(read_only=True)

    class Meta:
        model = ProductDocument
        fields = ("id", "document", "sort_order")


class ProductVariantListSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariant
        fields = (
            "id", "sku_code", "slug", "execution", "coil_type", "coil_voltage_v",
            "aux_contacts", "price", "stock_status", "is_default",
        )


class ProductVariantDetailSerializer(ProductVariantListSerializer):
    group_name = serializers.CharField(source="group.name", read_only=True)
    group_slug = serializers.CharField(source="group.slug", read_only=True)
    group_category_path = serializers.SerializerMethodField()
    dimensions = serializers.JSONField()
    documents = serializers.SerializerMethodField()
    specs = serializers.SerializerMethodField()

    class Meta(ProductVariantListSerializer.Meta):
        fields = ProductVariantListSerializer.Meta.fields + (
            "group_name", "group_slug", "group_category_path", "weight_net_kg", "weight_gross_kg",
            "dimensions", "documents", "specs",
        )

    def get_group_category_path(self, obj):
        if not obj.group.category_id:
            return []
        return category_path_slugs(obj.group.category)

    def get_specs(self, obj):
        specs = obj.group.specs.exclude(spec_key__in=PUBLIC_HIDDEN_SPEC_KEYS)
        return ProductSpecSerializer(specs, many=True).data

    def get_documents(self, obj):
        links = ProductDocument.objects.filter(
            models.Q(variant=obj) | models.Q(group=obj.group, variant__isnull=True),
            document__is_public=True,
        ).select_related("document")
        return ProductDocumentSerializer(links, many=True, context=self.context).data


class ProductGroupListSerializer(serializers.ModelSerializer):
    price_from = serializers.DecimalField(
        source="min_price", max_digits=12, decimal_places=2, read_only=True,
    )
    category_name = serializers.CharField(source="category.name", read_only=True)
    category_slug = serializers.CharField(source="category.slug", read_only=True)
    category_path = serializers.SerializerMethodField()
    primary_image = serializers.SerializerMethodField()
    default_variant = serializers.SerializerMethodField()
    variants_preview = serializers.SerializerMethodField()
    aux_contacts_options = serializers.SerializerMethodField()

    class Meta:
        model = ProductGroup
        fields = (
            "id", "name", "slug", "short_description", "series_code", "product_type",
            "nominal_current_a", "nominal_voltage_v", "poles", "honest_sign", "is_featured",
            "image_rotation",
            "price_from", "category_name", "category_slug", "category_path", "primary_image",
            "default_variant", "variants_preview", "aux_contacts_options",
        )

    def get_category_path(self, obj):
        return category_path_slugs(obj.category)

    def get_primary_image(self, obj):
        from apps.products.product_media import safe_image_url

        img = obj.images.filter(is_primary=True).first() or obj.images.first()
        if img and img.image:
            url = safe_image_url(img.image, self.context.get("request"))
            if url:
                return {"url": url, "alt": img.alt or obj.name}
        return {"url": "/placeholder-product.svg", "alt": obj.name, "is_placeholder": True}

    def get_default_variant(self, obj):
        variant = obj.variants.filter(is_active=True, is_default=True).first()
        if not variant:
            variant = obj.variants.filter(is_active=True).order_by("price").first()
        if variant:
            return ProductVariantListSerializer(variant).data
        return None

    def get_variants_preview(self, obj):
        """One variant per (coil, aux) — execution is a separate product card."""
        picked: list[ProductVariant] = []
        seen: set[tuple] = set()
        for variant in obj.variants.filter(is_active=True).order_by(
            "coil_voltage_v", "aux_contacts", "price",
        ):
            key = (variant.coil_voltage_v, variant.aux_contacts or "")
            if key in seen:
                continue
            seen.add(key)
            picked.append(variant)
            if len(picked) >= 64:
                break
        return ProductVariantListSerializer(picked, many=True).data

    def get_aux_contacts_options(self, obj):
        return list(
            obj.variants.filter(is_active=True)
            .exclude(aux_contacts="")
            .values_list("aux_contacts", flat=True)
            .distinct()
            .order_by("aux_contacts")
        )


class ProductGroupDetailSerializer(ProductGroupListSerializer):
    variants = ProductVariantListSerializer(many=True, read_only=True)
    specs = serializers.SerializerMethodField()
    images = ProductImageSerializer(many=True, read_only=True)
    documents = ProductDocumentSerializer(many=True, read_only=True)
    related = serializers.SerializerMethodField()

    class Meta(ProductGroupListSerializer.Meta):
        fields = ProductGroupListSerializer.Meta.fields + (
            "full_description", "designation_structure",
            "meta_title", "meta_description", "h1",
            "variants", "specs", "images", "documents", "related",
        )

    def get_specs(self, obj):
        specs = obj.specs.exclude(spec_key__in=PUBLIC_HIDDEN_SPEC_KEYS)
        return ProductSpecSerializer(specs, many=True).data

    def get_related(self, obj):
        related = obj.related_groups.filter(is_active=True)[:6]
        return ProductGroupListSerializer(related, many=True, context=self.context).data


class CompareVariantSerializer(ProductVariantDetailSerializer):
    """Extended variant for compare table."""

    nominal_current_a = serializers.IntegerField(source="group.nominal_current_a", read_only=True)
    poles = serializers.IntegerField(source="group.poles", read_only=True)
    product_type = serializers.CharField(source="group.product_type", read_only=True)

    class Meta(ProductVariantDetailSerializer.Meta):
        fields = ProductVariantDetailSerializer.Meta.fields + (
            "nominal_current_a", "poles", "product_type",
        )


class CompareResponseSerializer(serializers.Serializer):
    variants = CompareVariantSerializer(many=True)
    spec_keys = serializers.ListField(child=serializers.CharField())
