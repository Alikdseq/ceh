from django.urls import path

from .views import CallbackLeadView, ContactLeadView

urlpatterns = [
    path("leads/contact/", ContactLeadView.as_view(), name="lead-contact"),
    path("leads/contact", ContactLeadView.as_view()),
    path("leads/callback/", CallbackLeadView.as_view(), name="lead-callback"),
    path("leads/callback", CallbackLeadView.as_view()),
]
