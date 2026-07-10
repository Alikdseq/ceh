from django.urls import path

from .views import RedirectResolveView, RobotsView, SitemapView

urlpatterns = [
    path("seo/sitemap.xml", SitemapView.as_view(), name="sitemap"),
    path("seo/robots.txt", RobotsView.as_view(), name="robots"),
    path("redirects/resolve/", RedirectResolveView.as_view(), name="redirect-resolve"),
]
