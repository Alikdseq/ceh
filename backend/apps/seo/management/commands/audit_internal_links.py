"""Audit internal link paths: sitemap, product_catalog_path, category MPTT."""

from __future__ import annotations

from datetime import date
from pathlib import Path
from urllib.parse import urlparse

from django.core.management.base import BaseCommand

from apps.products.models import Category, ProductGroup
from apps.products.services.catalog_path_resolve import find_group_by_catalog_segment
from apps.products.utils import category_path_slugs, get_public_category_ids, is_category_public, product_catalog_path
from apps.seo.services.sitemap import collect_urls


class Command(BaseCommand):
    help = "Validate internal URLs from sitemap and catalog path helpers"

    def add_arguments(self, parser):
        parser.add_argument("--output", type=str, default="")
        parser.add_argument("--fail-on-error", action="store_true")

    def handle(self, *args, **options):
        issues: list[str] = []
        rows: list[tuple[str, str, str]] = []

        for item in collect_urls():
            path = urlparse(item["loc"]).path
            status = self._check_path(path)
            rows.append((path, status, "" if status == "ok" else status))
            if status != "ok":
                issues.append(f"Sitemap: {path} — {status}")

        public_ids = get_public_category_ids()
        for group in ProductGroup.objects.filter(is_active=True, category_id__in=public_ids).select_related("category"):
            path = product_catalog_path(group)
            status = self._check_path(path)
            rows.append((path, status, f"product:{group.slug}"))
            if status != "ok":
                issues.append(f"Product: {path} — {status}")

        for cat in Category.objects.filter(is_active=True):
            if not is_category_public(cat):
                continue
            slugs = category_path_slugs(cat)
            path = f"/catalog/{'/'.join(slugs)}/"
            status = self._check_path(path)
            rows.append((path, status, f"category:{cat.slug}"))
            if status != "ok":
                issues.append(f"Category: {path} — {status}")

        output = options["output"] or f"data/reports/link-audit-{date.today():%Y%m%d}.csv"
        out_path = Path(output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        lines = ["path,status,source\n"] + [f"{p},{s},{src}\n" for p, s, src in rows]
        out_path.write_text("".join(lines), encoding="utf-8")
        self.stdout.write(f"Report: {out_path}")

        if issues:
            self.stdout.write(self.style.WARNING(f"Found {len(issues)} issue(s):"))
            for line in issues[:50]:
                self.stdout.write(f"  - {line}")
            if len(issues) > 50:
                self.stdout.write(f"  ... and {len(issues) - 50} more")
        else:
            self.stdout.write(self.style.SUCCESS("All internal links resolve correctly"))

        if options["fail_on_error"] and issues:
            raise SystemExit(1)

    def _check_path(self, path: str) -> str:
        if not path.startswith("/"):
            return "not_absolute"
        if path.startswith("/catalog/"):
            segments = [s for s in path.strip("/").split("/") if s]
            if len(segments) < 2:
                return "catalog_root_ok"
            slug_segments = segments[1:]
            last = slug_segments[-1]
            product = find_group_by_catalog_segment(last)
            if product:
                canonical = product_catalog_path(product).rstrip("/")
                if path.rstrip("/") != canonical:
                    return f"non_canonical_product (expected {canonical}/)"
                return "ok"
            for i in range(len(slug_segments), 0, -1):
                candidate = Category.objects.filter(slug=slug_segments[i - 1], is_active=True).first()
                if candidate and category_path_slugs(candidate) == slug_segments[:i]:
                    return "ok"
            return "unresolved_category"
        return "ok"
