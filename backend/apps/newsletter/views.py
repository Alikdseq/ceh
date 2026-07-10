from django.utils.decorators import method_decorator
from django.utils import timezone
from django_ratelimit.decorators import ratelimit
from rest_framework import status
from rest_framework.parsers import FormParser, JSONParser
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import SubscribeSerializer
from .services.newsletter import confirm_subscriber, subscribe_email, unsubscribe
from .models import NewsletterSubscriber


@method_decorator(ratelimit(key="ip", rate="5/h", method="POST", block=False), name="post")
class SubscribeView(APIView):
    """POST /api/v1/newsletter/subscribe/"""

    authentication_classes = []
    permission_classes = [AllowAny]
    parser_classes = [JSONParser, FormParser]

    def post(self, request):
        if getattr(request, "limited", False):
            return Response({"detail": "Слишком много запросов."}, status=status.HTTP_429_TOO_MANY_REQUESTS)
        serializer = SubscribeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        email = data["email"].lower().strip()
        existing = NewsletterSubscriber.objects.filter(email=email).first()
        was_active = existing and existing.status == NewsletterSubscriber.Status.ACTIVE
        subscriber = subscribe_email(email, data.get("name", ""))
        # Store explicit marketing consent + audit data (IP/UA/version)
        subscriber.marketing_accepted = True
        subscriber.marketing_accepted_at = subscriber.marketing_accepted_at or timezone.now()
        subscriber.privacy_policy_version = data.get("privacy_policy_version", "")[:50]
        forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
        subscriber.ip = (forwarded.split(",")[0].strip() if forwarded else request.META.get("REMOTE_ADDR"))
        subscriber.user_agent = (request.META.get("HTTP_USER_AGENT", "")[:500])
        subscriber.save(update_fields=[
            "marketing_accepted", "marketing_accepted_at",
            "privacy_policy_version", "ip", "user_agent",
        ])
        if was_active:
            return Response({"detail": "already_subscribed"}, status=status.HTTP_200_OK)
        return Response(
            {"detail": "confirm_email_sent"},
            status=status.HTTP_201_CREATED,
        )


class ConfirmView(APIView):
    """GET /api/v1/newsletter/confirm/{token}/"""

    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request, token):
        subscriber = confirm_subscriber(token)
        if not subscriber:
            return Response({"detail": "not_found"}, status=status.HTTP_404_NOT_FOUND)
        return Response({"detail": "confirmed", "email": subscriber.email})


class UnsubscribeView(APIView):
    """GET /api/v1/newsletter/unsubscribe/{token}/"""

    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request, token):
        subscriber = unsubscribe(token)
        if not subscriber:
            return Response({"detail": "not_found"}, status=status.HTTP_404_NOT_FOUND)
        return Response({"detail": "unsubscribed", "email": subscriber.email})
