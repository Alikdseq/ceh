from rest_framework import serializers

from apps.quotes.validators import validate_ru_phone

from .models import CallbackLead, ContactLead


class ContactLeadSerializer(serializers.ModelSerializer):
    website = serializers.CharField(required=False, allow_blank=True, write_only=True)
    privacy_accepted = serializers.BooleanField(write_only=True)
    privacy_policy_version = serializers.CharField(required=False, allow_blank=True, default="", write_only=True)

    class Meta:
        model = ContactLead
        fields = (
            "name", "email", "phone", "message",
            "privacy_accepted", "privacy_policy_version",
            "website",
        )

    def validate_phone(self, value):
        if not value:
            return ""
        return validate_ru_phone(value)

    def validate_privacy_accepted(self, value):
        if not value:
            raise serializers.ValidationError("Необходимо согласие на обработку персональных данных")
        return value

    def validate_website(self, value):
        if value:
            raise serializers.ValidationError("Spam detected")
        return value


class CallbackLeadSerializer(serializers.ModelSerializer):
    website = serializers.CharField(required=False, allow_blank=True, write_only=True)

    class Meta:
        model = CallbackLead
        fields = ("name", "phone", "preferred_time", "website")

    def validate_phone(self, value):
        return validate_ru_phone(value)

    def validate_website(self, value):
        if value:
            raise serializers.ValidationError("Spam detected")
        return value
