"""Validate public URLs: sitemap, redirects, catalog paths, static routes."""

from __future__ import annotations

from pathlib import Path
from urllib.parse import urlparse

from django.core.management.base import BaseCommand

from apps.content.models import CaseStudy, CityCategoryLanding, DeliveryCity, NewsPost
from apps.products.models import Category, ProductGroup
from apps.products.services.catalog_path_resolve import find_group_by_catalog_segment
from apps.products.utils import category_path_slugs, get_public_category_ids, is_category_public, product_catalog_path
from apps.seo.application_landings import APPLICATION_LANDING_SLUGS
from apps.seo.models import Redirect
from apps.seo.services.sitemap import STATIC_PATHS, collect_urls

# Next.js App Router pages that exist in frontend/src/app (path prefixes)
FRONTEND_STATIC_ROUTES = {
    "/",
    "/catalog/",
    "/pricelist/",
    "/about/",
    "/about/production/",
    "/about/certificates/",
    "/contacts/",
    "/support/",
    "/dealers/",
    "/partners/",
    "/shareholders/",
    "/news/",
    "/cases/",
    "/delivery/",
    "/privacy/",
    "/terms/",
    "/cookies/",
    "/applications/",
    "/cart/",
    "/compare/",
    "/search/",
    "/order/success/",
}


class Command(BaseCommand):
    help = "Audit sitemap URLs, redirect targets, and catalog path resolution"

    def add_arguments(self, parser):
        parser.add_argument("--fix-report", type=str, default="", help="Write report to file")
        parser.add_argument("--fail-on-error", action="store_true")

    def handle(self, *args, **options):
        issues: list[str] = []

        issues.extend(self._audit_static_routes())
        issues.extend(self._audit_catalog_categories())
        issues.extend(self._audit_catalog_products())
        issues.extend(self._audit_sitemap_urls())
        issues.extend(self._audit_redirect_targets())
        issues.extend(self._audit_delivery_landings())

        if issues:
            self.stdout.write(self.style.WARNING(f"Found {len(issues)} issue(s):"))
            for line in issues:
                self.stdout.write(f"  - {line}")
        else:
            self.stdout.write(self.style.SUCCESS("All audited URLs resolve correctly"))

        if options["fix_report"]:
            Path(options["fix_report"]).write_text("\n".join(issues) + "\n", encoding="utf-8")

        if options["fail_on_error"] and issues:
            raise SystemExit(1)

    def _audit_static_routes(self) -> list[str]:
        issues: list[str] = []
        for path, _, _ in STATIC_PATHS:
            if path.startswith("/applications/") and path != "/applications/":
                slug = path.strip("/").split("/")[-1]
                if slug not in APPLICATION_LANDING_SLUGS:
                    issues.append(f"Sitemap application missing slug: {path}")
                continue
            if path not in FRONTEND_STATIC_ROUTES:
                issues.append(f"Sitemap static path has no frontend route: {path}")
        return issues

    def _audit_catalog_categories(self) -> list[str]:
        issues: list[str] = []
        for cat in Category.objects.filter(is_active=True):
            if not is_category_public(cat):
                continue
            slugs = category_path_slugs(cat)
            # Simulate findCategoryByPath — every prefix must resolve
            for i in range(1, len(slugs) + 1):
                prefix = slugs[:i]
                node = Category.objects.filter(slug=prefix[-1], is_active=True).first()
                if not node:
                    issues.append(f"Category segment missing in DB: {'/'.join(prefix)}")
        return issues

    def _audit_catalog_products(self) -> list[str]:
        issues: list[str] = []
        public_ids = get_public_category_ids()
        for group in ProductGroup.objects.filter(is_active=True, category_id__in=public_ids).select_related("category"):
            if not (group.slug or "").strip():
                issues.append(f"Product missing slug: id={group.pk} name={group.name!r}")
                continue
            if not group.category or not is_category_public(group.category):
                issues.append(f"Product {group.slug} in non-public category")
                continue
            resolved = find_group_by_catalog_segment(group.slug)
            if not resolved or resolved.id != group.id:
                issues.append(f"Product slug not self-resolving: {group.slug}")
            path = product_catalog_path(group)
            segments = [s for s in path.strip("/").split("/") if s]
            product_segment = segments[-1]
            cat_segments = segments[1:-1]
            if find_group_by_catalog_segment(product_segment) is None:
                issues.append(f"Product URL last segment does not resolve: {path}")
            if cat_segments:
                cat = Category.objects.filter(slug=cat_segments[-1], is_active=True).first()
                if not cat:
                    issues.append(f"Product category path invalid: {path}")
        return issues

    def _audit_sitemap_urls(self) -> list[str]:
        issues: list[str] = []
        for item in collect_urls():
            loc = item["loc"]
            path = urlparse(loc).path
            if not path.endswith("/") and not path.count("/") == 2 and not path.startswith("/news/"):
                pass
            if path.startswith("/news/") and path.rstrip("/").count("/") >= 2:
                slug = path.rstrip("/").split("/")[-1]
                if not NewsPost.objects.filter(slug=slug, is_published=True).exists():
                    issues.append(f"Sitemap news URL missing post: {path}")
            elif path.startswith("/cases/") and path.rstrip("/").count("/") >= 2:
                slug = path.strip("/").split("/")[-1]
                if not CaseStudy.objects.filter(slug=slug, is_published=True).exists():
                    issues.append(f"Sitemap case URL missing study: {path}")
            elif path.startswith("/delivery/") and path.count("/") >= 3:
                parts = [p for p in path.strip("/").split("/") if p]
                if len(parts) == 3 and parts[0] == "delivery":
                    city_slug, cat_slug = parts[1], parts[2]
                    landing = CityCategoryLanding.objects.filter(
                        city__slug=city_slug,
                        category__slug=cat_slug,
                        is_indexable=True,
                    ).exists()
                    if not landing:
                        issues.append(f"Sitemap delivery landing missing: {path}")
            elif path.startswith("/catalog/"):
                self._check_catalog_path(path, issues)
        return issues

    def _check_catalog_path(self, path: str, issues: list[str]) -> None:
        segments = [s for s in path.strip("/").split("/") if s]
        if len(segments) < 2:
            return
        slug_segments = segments[1:]
        last = slug_segments[-1]
        product = find_group_by_catalog_segment(last)
        if product:
            canonical = product_catalog_path(product).rstrip("/")
            if path.rstrip("/") != canonical:
                redirect = Redirect.objects.filter(
                    old_path__in=[path.rstrip("/"), path.rstrip("/") + "/"],
                    is_active=True,
                ).first()
                if not redirect or redirect.new_path.rstrip("/") != canonical:
                    issues.append(f"Sitemap product non-canonical without redirect: {path} → {canonical}/")
            return
        # Category listing
        cat = None
        for i in range(len(slug_segments), 0, -1):
            candidate = Category.objects.filter(slug=slug_segments[i - 1], is_active=True).first()
            if candidate and category_path_slugs(candidate) == slug_segments[:i]:
                cat = candidate
                break
        if not cat:
            redirect = Redirect.objects.filter(old_path=path.rstrip("/"), is_active=True).first()
            if not redirect:
                issues.append(f"Sitemap catalog path does not resolve: {path}")

    def _audit_redirect_targets(self) -> list[str]:
        issues: list[str] = []
        for redirect in Redirect.objects.filter(is_active=True).iterator():
            target = redirect.new_path
            if not target.startswith("/"):
                issues.append(f"Redirect target not absolute: {redirect.old_path} → {target}")
                continue
            if target.startswith("/pages/"):
                issues.append(f"Redirect target has no frontend route: {redirect.old_path} → {target}")
            if target.rstrip("/") == redirect.old_path.rstrip("/"):
                issues.append(f"Redirect loop: {redirect.old_path} → {target}")
        return issues

    def _audit_delivery_landings(self) -> list[str]:
        issues: list[str] = []
        for landing in CityCategoryLanding.objects.filter(is_indexable=True).select_related("city", "category"):
            if not DeliveryCity.objects.filter(slug=landing.city.slug, is_indexable=True).exists():
                issues.append(f"Landing city not indexable: {landing.city.slug}")
            if not is_category_public(landing.category):
                issues.append(f"Landing category not public: {landing.category.slug}")
        return issues
