from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

import config.admin_custom  # noqa: F401 — unfold user admin

admin_url = settings.ADMIN_URL.strip("/")

urlpatterns = [
    path(f"{admin_url}/", admin.site.urls),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/v1/", include("config.api_urls")),
]
