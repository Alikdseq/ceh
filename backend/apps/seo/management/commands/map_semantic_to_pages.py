"""Map semantic-core.yaml queries to catalog URLs and meta coverage."""

from __future__ import annotations

from pathlib import Path

import yaml
from django.core.management.base import BaseCommand

from apps.products.models import ProductGroup
from apps.products.utils import product_catalog_path


class Command(BaseCommand):
    help = "Report semantic-core query → URL mapping and meta fill status."

    def add_arguments(self, parser):
        parser.add_argument(
            "--file",
            type=str,
            default="data/seo/semantic-core.yaml",
            help="Path to semantic core YAML (repo root relative)",
        )

    def handle(self, *args, **options):
        from django.conf import settings

        root = Path(settings.BASE_DIR).parent
        path = Path(options["file"])
        if not path.is_absolute():
            path = root / path
        if not path.is_file():
            self.stderr.write(f"File not found: {path}")
            return

        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        rows: list[tuple[str, str, str, str]] = []

        for _cluster_name, cluster in (data.get("clusters") or {}).items():
            priority = cluster.get("priority", "P2")
            for item in cluster.get("queries") or []:
                query = item.get("query", "")
                target = item.get("target_url") or item.get("target_url_pattern") or "—"
                status = self._resolve_status(item)
                rows.append((priority, query, target, status))

        rows.sort(key=lambda r: (r[0], r[1]))
        for priority, query, target, status in rows:
            self.stdout.write(f"[{priority}] {query}\n  → {target}\n  {status}\n")

    def _resolve_status(self, item: dict) -> str:
        series = item.get("series")
        target_url = item.get("target_url")
        page_type = item.get("page_type")

        if page_type in ("home", "static", "cms", "landing", "news", "news_list", "catalog_root"):
            return "static/cms page — verify meta in CMS or frontend"

        if series:
            group = (
                ProductGroup.objects.filter(is_active=True, series_code=series)
                .order_by("sort_order")
                .first()
            )
            if not group:
                return "MISSING: no active ProductGroup for series"
            url = product_catalog_path(group)
            meta_ok = bool(group.meta_title and group.meta_description)
            return f"OK {url} meta={'filled' if meta_ok else 'INCOMPLETE'}"

        if target_url and target_url.startswith("/catalog/"):
            return "verify category/product slug manually"

        return "manual check"
