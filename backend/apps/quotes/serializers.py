from rest_framework import serializers

from .validators import validate_inn, validate_kpp, validate_ru_phone


class CartItemAddSerializer(serializers.Serializer):
    variant_id = serializers.IntegerField(min_value=1)
    quantity = serializers.IntegerField(min_value=1, max_value=9999, default=1)


class CartItemUpdateSerializer(serializers.Serializer):
    quantity = serializers.IntegerField(min_value=0, max_value=9999)


class QuoteCreateSerializer(serializers.Serializer):
    contact_name = serializers.CharField(max_length=255)
    company_name = serializers.CharField(max_length=255)
    email = serializers.EmailField()
    phone = serializers.CharField(max_length=30)
    city = serializers.CharField(max_length=100, required=False, allow_blank=True, default="")
    inn = serializers.CharField(max_length=12, required=False, allow_blank=True, default="")
    kpp = serializers.CharField(max_length=9, required=False, allow_blank=True, default="")
    comment = serializers.CharField(required=False, allow_blank=True, default="")
    privacy_accepted = serializers.BooleanField()
    privacy_policy_version = serializers.CharField(max_length=50, required=False, allow_blank=True, default="")
    website = serializers.CharField(required=False, allow_blank=True, default="")
    utm_source = serializers.CharField(max_length=100, required=False, allow_blank=True, default="")
    utm_medium = serializers.CharField(max_length=100, required=False, allow_blank=True, default="")
    utm_campaign = serializers.CharField(max_length=100, required=False, allow_blank=True, default="")

    def validate_phone(self, value):
        return validate_ru_phone(value)

    def validate_inn(self, value):
        return validate_inn(value)

    def validate_kpp(self, value):
        return validate_kpp(value)

    def validate_privacy_accepted(self, value):
        if not value:
            raise serializers.ValidationError("Необходимо согласие на обработку персональных данных")
        return value

    def validate_website(self, value):
        if value:
            raise serializers.ValidationError("Spam detected")
        return value
