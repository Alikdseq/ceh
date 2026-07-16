from django.urls import path

from .views import (
    CaseStudyDetailView,
    CaseStudyListView,
    CityCategoryLandingView,
    CorporateDocumentDownloadView,
    CorporateDocumentListView,
    DeliveryCityDetailView,
    DeliveryCityListView,
    FAQListView,
    NewsDetailView,
    NewsListView,
    NewsRSSView,
    PageDetailView,
    PriceListPdfView,
    PriceListView,
    SiteSettingsView,
)

urlpatterns = [
    path("settings/", SiteSettingsView.as_view(), name="settings"),
    path("pages/<slug:slug>/", PageDetailView.as_view(), name="page-detail"),
    path("news/rss/", NewsRSSView.as_view(), name="news-rss"),
    path("news/", NewsListView.as_view(), name="news-list"),
    path("news/<slug:slug>/", NewsDetailView.as_view(), name="news-detail"),
    path("faq/", FAQListView.as_view(), name="faq-list"),
    path("cases/", CaseStudyListView.as_view(), name="case-list"),
    path("cases/<slug:slug>/", CaseStudyDetailView.as_view(), name="case-detail"),
    path("delivery/", DeliveryCityListView.as_view(), name="delivery-list"),
    path("delivery/<slug:slug>/", DeliveryCityDetailView.as_view(), name="delivery-detail"),
    path(
        "delivery/<slug:city_slug>/<slug:category_slug>/",
        CityCategoryLandingView.as_view(),
        name="delivery-category",
    ),
    path("pricelist/", PriceListView.as_view(), name="pricelist"),
    path("pricelist/export/pdf/", PriceListPdfView.as_view(), name="pricelist-pdf"),
    path("corporate-docs/download/", CorporateDocumentDownloadView.as_view(), name="corporate-doc-download"),
    path("corporate-docs/", CorporateDocumentListView.as_view(), name="corporate-doc-list"),
]
