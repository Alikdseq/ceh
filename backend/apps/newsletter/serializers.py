from django.conf import settings
from rest_framework import serializers

from .models import NewsletterSubscriber


class SubscribeSerializer(serializers.Serializer):
    email = serializers.EmailField()
    name = serializers.CharField(max_length=255, required=False, allow_blank=True, default="")
    marketing_accepted = serializers.BooleanField()
    privacy_policy_version = serializers.CharField(max_length=50, required=False, allow_blank=True, default="")
    website = serializers.CharField(required=False, allow_blank=True, default="")

    def validate_marketing_accepted(self, value):
        if not value:
            raise serializers.ValidationError("Необходимо согласие на получение рассылки и обработку персональных данных")
        return value

    def validate_website(self, value):
        if value:
            raise serializers.ValidationError("Spam detected")
        return value


class SubscriberSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsletterSubscriber
        fields = ("email", "name", "status", "subscribed_at", "confirmed_at")


def get_site_url() -> str:
    return getattr(settings, "FRONTEND_URL", "http://localhost:3000").rstrip("/")
