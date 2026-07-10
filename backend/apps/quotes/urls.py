from django.urls import path

from .views import (
    CartClearView,
    CartExportPdfView,
    CartExportXlsxView,
    CartItemCreateView,
    CartItemDetailView,
    CartView,
    QuoteCreateView,
)

urlpatterns = [
    # With and without trailing slash — Next.js proxy may strip the slash.
    path("cart/", CartView.as_view(), name="cart-detail"),
    path("cart", CartView.as_view()),
    path("cart/items/", CartItemCreateView.as_view(), name="cart-item-create"),
    path("cart/items", CartItemCreateView.as_view()),
    path("cart/items/<int:item_id>/", CartItemDetailView.as_view(), name="cart-item-detail"),
    path("cart/items/<int:item_id>", CartItemDetailView.as_view()),
    path("cart/clear/", CartClearView.as_view(), name="cart-clear"),
    path("cart/clear", CartClearView.as_view()),
    path("cart/export/pdf/", CartExportPdfView.as_view(), name="cart-export-pdf"),
    path("cart/export/pdf", CartExportPdfView.as_view()),
    path("cart/export/xlsx/", CartExportXlsxView.as_view(), name="cart-export-xlsx"),
    path("cart/export/xlsx", CartExportXlsxView.as_view()),
    path("quotes/", QuoteCreateView.as_view(), name="quote-create"),
    path("quotes", QuoteCreateView.as_view()),
]
