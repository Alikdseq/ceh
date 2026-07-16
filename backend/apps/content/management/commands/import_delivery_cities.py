from pathlib import Path

import yaml
from django.conf import settings
from django.core.management.base import BaseCommand

from apps.content.models import DeliveryCity


class Command(BaseCommand):
    help = "Import delivery cities from data/seo/cities.yaml"

    def add_arguments(self, parser):
        parser.add_argument(
            "--file",
            type=str,
            default="data/seo/cities.yaml",
        )
        parser.add_argument("--dry-run", action="store_true")

    def handle(self, *args, **options):
        root = Path(settings.BASE_DIR).parent
        path = root / options["file"]
        if not path.is_file():
            self.stderr.write(f"Not found: {path}")
            return

        payload = yaml.safe_load(path.read_text(encoding="utf-8"))
        created = updated = 0
        for row in payload.get("cities") or []:
            intro = (row.get("intro_html") or "").strip()
            indexable = bool(row.get("indexable")) and len(intro) >= 400
            defaults = {
                "name": row["name"],
                "region_name": row.get("region_name", ""),
                "priority": row.get("priority", 100),
                "is_indexable": indexable,
                "intro_html": intro,
                "meta_title": row.get("meta_title", ""),
                "meta_description": row.get("meta_description", ""),
            }
            if options["dry_run"]:
                self.stdout.write(f"Would upsert {row['slug']} indexable={indexable}")
                continue
            _obj, was_created = DeliveryCity.objects.update_or_create(
                slug=row["slug"],
                defaults=defaults,
            )
            if was_created:
                created += 1
            else:
                updated += 1

        self.stdout.write(self.style.SUCCESS(f"Created {created}, updated {updated}"))
