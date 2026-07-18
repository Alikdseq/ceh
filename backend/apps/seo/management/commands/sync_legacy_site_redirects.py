"""Bulk-create Redirect rows for legacy CMS paths (/company/*, /files/*)."""

from django.core.management.base import BaseCommand

from apps.seo.models import Redirect
from apps.seo.services.legacy_paths import collect_legacy_redirect_pairs


class Command(BaseCommand):
    help = "Sync Redirect rows for legacy /company/*, /files/* and old catalog sections"

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", action="store_true")

    def handle(self, *args, **options):
        pairs = collect_legacy_redirect_pairs()
        created = updated = 0
        for old_path, new_path in pairs:
            if options["dry_run"]:
                self.stdout.write(f"  {old_path} → {new_path}")
                continue
            _, was_created = Redirect.objects.update_or_create(
                old_path=old_path,
                defaults={"new_path": new_path, "is_active": True},
            )
            if was_created:
                created += 1
            else:
                updated += 1

        if options["dry_run"]:
            self.stdout.write(self.style.SUCCESS(f"Would sync {len(pairs)} legacy redirect(s)"))
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Legacy redirects: {created} created, {updated} updated ({len(pairs)} total)"
                )
            )
