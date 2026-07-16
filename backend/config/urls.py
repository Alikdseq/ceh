from django.conf import settings
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.static import serve
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

import config.admin_custom  # noqa: F401 — unfold user admin

admin_url = settings.ADMIN_URL.strip("/")

urlpatterns = [
    path(f"{admin_url}/", admin.site.urls),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/v1/", include("config.api_urls")),
]

# User uploads (ProductImage, CMS). Nginx proxies /media/ to gunicorn in production.
urlpatterns += [
    re_path(
        r"^media/(?P<path>.*)$",
        serve,
        {"document_root": settings.MEDIA_ROOT},
    ),
]
