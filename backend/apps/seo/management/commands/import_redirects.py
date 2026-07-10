import csv
from pathlib import Path

from django.core.management.base import BaseCommand

from apps.seo.models import Redirect


class Command(BaseCommand):
    help = "Import 301 redirects from CSV: old_path,new_path (STEP-103)"

    def add_arguments(self, parser):
        parser.add_argument("csv_path", type=str, help="Path to redirects CSV")

    def handle(self, *args, **options):
        path = Path(options["csv_path"])
        if not path.exists():
            self.stderr.write(f"File not found: {path}")
            return

        created = updated = 0
        with path.open(encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                old_path = row.get("old_path", row.get("old_url", "")).strip()
                new_path = row.get("new_path", row.get("new_url", "")).strip()
                if not old_path or not new_path:
                    continue
                if not old_path.startswith("/"):
                    old_path = f"/{old_path}"
                obj, was_created = Redirect.objects.update_or_create(
                    old_path=old_path,
                    defaults={"new_path": new_path, "is_active": True},
                )
                if was_created:
                    created += 1
                else:
                    updated += 1

        self.stdout.write(self.style.SUCCESS(f"Redirects: {created} created, {updated} updated"))
