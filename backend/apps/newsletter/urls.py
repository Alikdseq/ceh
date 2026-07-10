from django.urls import path

from .views import ConfirmView, SubscribeView, UnsubscribeView

urlpatterns = [
    # With and without trailing slash — Next.js rewrite may strip the slash on proxy.
    path("newsletter/subscribe/", SubscribeView.as_view(), name="newsletter-subscribe"),
    path("newsletter/subscribe", SubscribeView.as_view()),
    path("newsletter/confirm/<uuid:token>/", ConfirmView.as_view(), name="newsletter-confirm"),
    path("newsletter/confirm/<uuid:token>", ConfirmView.as_view()),
    path("newsletter/unsubscribe/<uuid:token>/", UnsubscribeView.as_view(), name="newsletter-unsubscribe"),
    path("newsletter/unsubscribe/<uuid:token>", UnsubscribeView.as_view()),
]
