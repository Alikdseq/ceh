from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Redirect
from .services.sitemap import build_robots_txt, build_sitemap_xml, write_sitemap_file


class SitemapView(APIView):
    """GET /api/v1/seo/sitemap.xml — or mounted at root via urls."""

    authentication_classes = []
    permission_classes = []

    def get(self, request):
        path = settings.MEDIA_ROOT / "sitemap.xml"
        if not path.exists():
            write_sitemap_file()
        content = path.read_bytes() if path.exists() else build_sitemap_xml()
        return HttpResponse(content, content_type="application/xml; charset=utf-8")


class RobotsView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        return HttpResponse(build_robots_txt(), content_type="text/plain; charset=utf-8")


class RedirectResolveView(APIView):
    """GET /api/v1/redirects/resolve/?path=/old-url/"""

    authentication_classes = []
    permission_classes = []

    def get(self, request):
        path = request.query_params.get("path", "").strip()
        if not path.startswith("/"):
            path = f"/{path}"
        redirect = Redirect.objects.filter(old_path=path, is_active=True).first()
        if not redirect:
            redirect = Redirect.objects.filter(old_path=path.rstrip("/"), is_active=True).first()
        if not redirect and not path.endswith("/"):
            redirect = Redirect.objects.filter(old_path=f"{path}/", is_active=True).first()
        if redirect:
            return Response({"new_path": redirect.new_path, "status": 301})
        return Response({"new_path": None})
