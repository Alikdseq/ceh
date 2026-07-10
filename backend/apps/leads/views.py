from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import CallbackLeadSerializer, ContactLeadSerializer
from .services.leads import create_callback_lead, create_contact_lead


@method_decorator(ratelimit(key="ip", rate="5/h", method="POST", block=False), name="post")
class ContactLeadView(APIView):
    """POST /api/v1/leads/contact/"""

    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        if getattr(request, "limited", False):
            return Response(
                {"detail": "Слишком много обращений. Попробуйте позже."},
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )
        serializer = ContactLeadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        create_contact_lead(serializer.validated_data, request)
        return Response({"detail": "ok"}, status=status.HTTP_201_CREATED)


@method_decorator(ratelimit(key="ip", rate="5/h", method="POST", block=False), name="post")
class CallbackLeadView(APIView):
    """POST /api/v1/leads/callback/"""

    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        if getattr(request, "limited", False):
            return Response(
                {"detail": "Слишком много обращений. Попробуйте позже."},
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )
        serializer = CallbackLeadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        create_callback_lead(serializer.validated_data, request)
        return Response({"detail": "ok"}, status=status.HTTP_201_CREATED)
