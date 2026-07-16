from rest_framework import serializers

from apps.core.pricing import price_without_vat_display

from .models import (
    CaseStudy,
    CityCategoryLanding,
    DeliveryCity,
    FAQItem,
    NewsPost,
    Page,
    PriceListItem,
    PriceListSection,
    SiteSettings,
)
from apps.products.serializers import ProductGroupListSerializer


class SiteSettingsSerializer(serializers.ModelSerializer):
    order_emails_list = serializers.ListField(
        source="get_order_emails_list", read_only=True,
    )

    class Meta:
        model = SiteSettings
        fields = (
            "company_name", "phone_main", "phone_sales", "email_main",
            "order_emails_list", "address", "requisites",
            "yandex_metrika_id", "ga4_id",
        )


class PageDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Page
        fields = (
            "title", "slug", "body", "meta_title", "meta_description",
            "h1", "updated_at",
        )


class NewsPostListSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsPost
        fields = (
            "id", "title", "slug", "excerpt", "published_at",
        )


class NewsPostDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsPost
        fields = (
            "title", "slug", "excerpt", "body", "meta_title",
            "meta_description", "published_at",
        )


class FAQItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQItem
        fields = ("id", "category", "question", "answer", "sort_order")


class PriceListItemSerializer(serializers.ModelSerializer):
    price_without_vat = serializers.SerializerMethodField()

    class Meta:
        model = PriceListItem
        fields = (
            "id",
            "name",
            "price",
            "price_without_vat",
            "nominal_current_a",
            "product_type",
            "notes",
            "sort_order",
        )

    def get_price_without_vat(self, obj):
        return price_without_vat_display(obj.price)


class PriceListSectionSerializer(serializers.ModelSerializer):
    items = serializers.SerializerMethodField()

    class Meta:
        model = PriceListSection
        fields = ("id", "name", "sort_order", "items")

    def get_items(self, obj):
        items = obj.items.filter(is_active=True).order_by("sort_order", "name")
        return PriceListItemSerializer(items, many=True).data


class CaseStudyListSerializer(serializers.ModelSerializer):
    class Meta:
        model = CaseStudy
        fields = ("title", "slug", "excerpt", "industry", "published_at")


class CaseStudyDetailSerializer(serializers.ModelSerializer):
    products = ProductGroupListSerializer(many=True, read_only=True)

    class Meta:
        model = CaseStudy
        fields = (
            "title",
            "slug",
            "excerpt",
            "body",
            "industry",
            "meta_title",
            "meta_description",
            "published_at",
            "products",
        )


class DeliveryCityListSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryCity
        fields = ("slug", "name", "region_name", "priority", "is_indexable")


class DeliveryCityDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryCity
        fields = (
            "slug",
            "name",
            "region_name",
            "is_indexable",
            "intro_html",
            "meta_title",
            "meta_description",
        )


class CityCategoryLandingSerializer(serializers.ModelSerializer):
    city_slug = serializers.CharField(source="city.slug", read_only=True)
    category_slug = serializers.CharField(source="category.slug", read_only=True)
    category_name = serializers.CharField(source="category.name", read_only=True)

    class Meta:
        model = CityCategoryLanding
        fields = (
            "city_slug",
            "category_slug",
            "category_name",
            "intro_html",
            "is_indexable",
            "meta_title",
            "meta_description",
        )
