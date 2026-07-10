from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.utils import timezone
from django_ratelimit.decorators import ratelimit
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import CartItemAddSerializer, CartItemUpdateSerializer, QuoteCreateSerializer
from .services.cart import (
    add_item,
    attach_session,
    clear_cart,
    get_or_create_cart,
    remove_item,
    resolve_session_key,
    serialize_cart,
    update_item,
)
from .services.exports import render_cart_pdf, render_cart_xlsx
from .services.quotes import create_quote_from_cart


def _client_ip(request) -> str:
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "127.0.0.1")


class CartMixin:
    def get_cart(self, request):
        session_key, is_new = resolve_session_key(request)
        cart = get_or_create_cart(session_key, user=request.user if request.user.is_authenticated else None)
        return cart, session_key, is_new

    def cart_response(self, request, cart, session_key, is_new, status_code=status.HTTP_200_OK):
        data = serialize_cart(cart, request)
        response = Response(data, status=status_code)
        attach_session(response, session_key, is_new)
        return response


class CartView(CartMixin, APIView):
    """GET /api/v1/cart/ — list + subtotal."""

    def get(self, request):
        cart, session_key, is_new = self.get_cart(request)
        return self.cart_response(request, cart, session_key, is_new)


class CartItemCreateView(CartMixin, APIView):
    """POST /api/v1/cart/items/ — add variant."""

    def post(self, request):
        serializer = CartItemAddSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        cart, session_key, is_new = self.get_cart(request)
        try:
            add_item(
                cart,
                serializer.validated_data["variant_id"],
                serializer.validated_data.get("quantity", 1),
            )
        except ValueError:
            return Response({"detail": "Variant not found"}, status=status.HTTP_404_NOT_FOUND)
        cart.refresh_from_db()
        return self.cart_response(request, cart, session_key, is_new, status.HTTP_201_CREATED)


class CartItemDetailView(CartMixin, APIView):
    """PATCH/DELETE /api/v1/cart/items/{id}/"""

    def patch(self, request, item_id):
        serializer = CartItemUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        cart, session_key, is_new = self.get_cart(request)
        result = update_item(cart, item_id, serializer.validated_data["quantity"])
        if result is None and serializer.validated_data["quantity"] > 0:
            return Response({"detail": "Item not found"}, status=status.HTTP_404_NOT_FOUND)
        cart.refresh_from_db()
        return self.cart_response(request, cart, session_key, is_new)

    def delete(self, request, item_id):
        cart, session_key, is_new = self.get_cart(request)
        if not remove_item(cart, item_id):
            return Response({"detail": "Item not found"}, status=status.HTTP_404_NOT_FOUND)
        cart.refresh_from_db()
        return self.cart_response(request, cart, session_key, is_new)


class CartClearView(CartMixin, APIView):
    """DELETE /api/v1/cart/clear/"""

    def delete(self, request):
        cart, session_key, is_new = self.get_cart(request)
        clear_cart(cart)
        cart.refresh_from_db()
        return self.cart_response(request, cart, session_key, is_new)


class CartExportPdfView(CartMixin, APIView):
    """GET /api/v1/cart/export/pdf/"""

    def get(self, request):
        cart, _, _ = self.get_cart(request)
        if not cart.items.exists():
            return Response({"detail": "Cart is empty"}, status=status.HTTP_400_BAD_REQUEST)
        pdf = render_cart_pdf(cart)
        response = HttpResponse(pdf, content_type="application/pdf")
        response["Content-Disposition"] = 'inline; filename="specification.pdf"'
        return response


class CartExportXlsxView(CartMixin, APIView):
    """GET /api/v1/cart/export/xlsx/"""

    def get(self, request):
        cart, _, _ = self.get_cart(request)
        if not cart.items.exists():
            return Response({"detail": "Cart is empty"}, status=status.HTTP_400_BAD_REQUEST)
        xlsx = render_cart_xlsx(cart)
        response = HttpResponse(
            xlsx,
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        response["Content-Disposition"] = 'attachment; filename="specification.xlsx"'
        return response


@method_decorator(ratelimit(key="ip", rate="5/h", method="POST", block=False), name="post")
class QuoteCreateView(CartMixin, APIView):
    """POST /api/v1/quotes/ — submit quote from cart."""

    def post(self, request):
        if getattr(request, "limited", False):
            return Response(
                {"detail": "Слишком много заявок. Попробуйте позже."},
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )

        serializer = QuoteCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        cart, session_key, is_new = self.get_cart(request)
        if not cart.items.exists():
            return Response({"detail": "Cart is empty"}, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        try:
            quote = create_quote_from_cart(
                cart,
                contact_name=data["contact_name"],
                company_name=data["company_name"],
                email=data["email"],
                phone=data["phone"],
                city=data.get("city", ""),
                inn=data.get("inn", ""),
                kpp=data.get("kpp", ""),
                comment=data.get("comment", ""),
                ip=_client_ip(request),
                user_agent=request.META.get("HTTP_USER_AGENT", "")[:500],
                utm_source=data.get("utm_source", ""),
                utm_medium=data.get("utm_medium", ""),
                utm_campaign=data.get("utm_campaign", ""),
            )
        except ValueError:
            return Response({"detail": "Cart is empty"}, status=status.HTTP_400_BAD_REQUEST)

        quote.privacy_accepted = True
        quote.privacy_accepted_at = timezone.now()
        quote.privacy_policy_version = data.get("privacy_policy_version", "")[:50]
        quote.save(update_fields=["privacy_accepted", "privacy_accepted_at", "privacy_policy_version"])

        from .tasks import process_new_quote
        process_new_quote.delay(quote.pk)

        response = Response({"number": quote.number}, status=status.HTTP_201_CREATED)
        attach_session(response, session_key, is_new)
        return response
