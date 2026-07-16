"""Copy catalog photos from frontend/public/tovar into MEDIA_ROOT/products (prod deploy)."""
from __future__ import annotations

import shutil
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from apps.products.catalog_static_photos import _IMAGE_SUFFIXES


class Command(BaseCommand):
    help = "Sync static catalog photos into Django media (fixes /media/products/ 404 on prod)"

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", action="store_true")

    def handle(self, *args, **options):
        src_dir = Path(settings.CATALOG_TOVAR_DIR)
        if not src_dir.is_dir():
            self.stdout.write(self.style.WARNING(f"Catalog dir missing: {src_dir}"))
            return

        dest_dir = Path(settings.MEDIA_ROOT) / "products"
        dest_dir.mkdir(parents=True, exist_ok=True)

        copied = 0
        skipped = 0
        for entry in sorted(src_dir.iterdir()):
            if not entry.is_file() or entry.suffix.lower() not in _IMAGE_SUFFIXES:
                continue
            target = dest_dir / entry.name
            if target.exists() and target.stat().st_size == entry.stat().st_size:
                skipped += 1
                continue
            if options["dry_run"]:
                self.stdout.write(f"  would copy {entry.name}")
                copied += 1
                continue
            shutil.copy2(entry, target)
            copied += 1

        if options["dry_run"]:
            self.stdout.write(self.style.SUCCESS(f"Would copy {copied} file(s), skip {skipped}"))
        else:
            self.stdout.write(
                self.style.SUCCESS(f"Synced {copied} catalog photo(s) to media/products ({skipped} unchanged)")
            )
