from django.urls import include, path

urlpatterns = [
    path("", include("apps.products.urls")),
    path("", include("apps.content.urls")),
    path("", include("apps.quotes.urls")),
    path("", include("apps.leads.urls")),
    path("", include("apps.newsletter.urls")),
    path("", include("apps.seo.urls")),
]
