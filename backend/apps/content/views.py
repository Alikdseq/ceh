import html
from pathlib import Path

from django.conf import settings
from django.http import FileResponse, Http404, HttpResponse
from django.utils.encoding import smart_str
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import FAQItem, NewsPost, Page, SiteSettings
from .serializers import (
    FAQItemSerializer,
    NewsPostDetailSerializer,
    NewsPostListSerializer,
    PageDetailSerializer,
    PriceListSectionSerializer,
    SiteSettingsSerializer,
)
from .services.pricelist import render_price_list_pdf

CORPORATE_DOC_CATEGORIES = {"affilr", "raskrinfo", "charter"}


def _docs_root() -> Path:
    env_root = getattr(settings, "CORPORATE_DOCS_ROOT", None)
    if env_root:
        return Path(env_root)
    return Path(settings.BASE_DIR).parent / "docs"


class SiteSettingsView(APIView):
    """GET /api/v1/settings/"""

    def get(self, request):
        return Response(SiteSettingsSerializer(SiteSettings.load()).data)


class PageDetailView(generics.RetrieveAPIView):
    """GET /api/v1/pages/{slug}/"""

    serializer_class = PageDetailSerializer
    lookup_field = "slug"

    def get_queryset(self):
        return Page.objects.filter(is_published=True)


class NewsListView(generics.ListAPIView):
    """GET /api/v1/news/"""

    serializer_class = NewsPostListSerializer

    def get_queryset(self):
        return NewsPost.objects.filter(is_published=True)


class NewsDetailView(generics.RetrieveAPIView):
    """GET /api/v1/news/{slug}/"""

    serializer_class = NewsPostDetailSerializer
    lookup_field = "slug"

    def get_queryset(self):
        return NewsPost.objects.filter(is_published=True)


class FAQListView(generics.ListAPIView):
    """GET /api/v1/faq/"""

    serializer_class = FAQItemSerializer

    def get_queryset(self):
        return FAQItem.objects.filter(is_published=True)


class PriceListView(APIView):
    """GET /api/v1/pricelist/ — public price list table."""

    def get(self, request):
        from .models import PriceListSection

        sections = (
            PriceListSection.objects.filter(is_active=True)
            .prefetch_related("items")
            .order_by("sort_order", "name")
        )
        data = PriceListSectionSerializer(sections, many=True).data
        return Response(data)


class PriceListPdfView(APIView):
    """GET /api/v1/pricelist/export/pdf/"""

    def get(self, request):
        pdf = render_price_list_pdf()
        response = HttpResponse(pdf, content_type="application/pdf")
        response["Content-Disposition"] = 'attachment; filename="pricelist.pdf"'
        return response


class CorporateDocumentListView(APIView):
    """GET /api/v1/corporate-docs/?category=raskrinfo"""

    def get(self, request):
        category = (request.query_params.get("category") or "").strip().lower()
        if category not in {"affilr", "raskrinfo"}:
            return Response([])

        root = _docs_root() / category
        if not root.exists():
            return Response([])

        items = []
        for path in sorted(root.iterdir(), key=lambda item: item.name.lower(), reverse=True):
            if not path.is_file():
                continue
            items.append({
                "label": path.stem.replace("_", " "),
                "file": path.name,
                "size_kb": max(1, round(path.stat().st_size / 1024)),
            })
        return Response(items)


class CorporateDocumentDownloadView(APIView):
    """GET /api/v1/corporate-docs/download/?category=affilr&file=name.docx"""

    def get(self, request):
        category = (request.query_params.get("category") or "").strip().lower()
        filename = (request.query_params.get("file") or "").strip()
        if category not in CORPORATE_DOC_CATEGORIES or not filename:
            return Response({"detail": "Invalid request"}, status=status.HTTP_400_BAD_REQUEST)
        if ".." in filename or "/" in filename or "\\" in filename:
            return Response({"detail": "Invalid file"}, status=status.HTTP_400_BAD_REQUEST)

        if category == "charter":
            path = _docs_root() / "charter" / filename
        else:
            path = _docs_root() / category / filename

        if not path.exists() or not path.is_file():
            raise Http404("Document not found")

        return FileResponse(
            path.open("rb"),
            as_attachment=True,
            filename=smart_str(path.name),
        )


class NewsRSSView(APIView):
    """GET /api/v1/news/rss/ — RSS 2.0 feed."""

    def get(self, request):
        posts = NewsPost.objects.filter(is_published=True).order_by("-published_at")[:50]
        site_url = request.build_absolute_uri("/").replace("/api/v1/news/rss/", "").rstrip("/")
        if "8000" in site_url:
            site_url = "http://localhost:3000"
        lines = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">',
            "<channel>",
            "<title>Новости — Электроконтактор</title>",
            f"<link>{site_url}/news</link>",
            "<description>Новости АО «Электроконтактор»</description>",
            f'<atom:link href="{request.build_absolute_uri()}" rel="self" type="application/rss+xml"/>',
        ]
        for post in posts:
            link = f"{site_url}/news/{post.slug}"
            lines += [
                "<item>",
                f"<title>{html.escape(post.title)}</title>",
                f"<link>{link}</link>",
                f"<guid isPermaLink=\"true\">{link}</guid>",
                f"<pubDate>{post.published_at.strftime('%a, %d %b %Y %H:%M:%S +0300')}</pubDate>",
                f"<description>{html.escape(post.excerpt)}</description>",
                "</item>",
            ]
        lines += ["</channel>", "</rss>"]
        return HttpResponse("\n".join(lines), content_type="application/rss+xml; charset=utf-8")
