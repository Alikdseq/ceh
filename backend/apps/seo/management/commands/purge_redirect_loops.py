"""Deactivate Redirect rows where old_path equals new_path (redirect loops)."""

from django.core.management.base import BaseCommand

from apps.seo.models import Redirect
from apps.seo.services.redirect_resolve import paths_equivalent


class Command(BaseCommand):
    help = "Deactivate self-referential Redirect rows that cause ERR_TOO_MANY_REDIRECTS"

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", action="store_true")

    def handle(self, *args, **options):
        deactivated = 0
        for redirect in Redirect.objects.filter(is_active=True).iterator():
            if paths_equivalent(redirect.old_path, redirect.new_path):
                if options["dry_run"]:
                    self.stdout.write(f"  loop: {redirect.old_path} → {redirect.new_path}")
                else:
                    redirect.is_active = False
                    redirect.save(update_fields=["is_active"])
                deactivated += 1

        if options["dry_run"]:
            self.stdout.write(self.style.WARNING(f"Would deactivate {deactivated} loop redirect(s)"))
        else:
            self.stdout.write(self.style.SUCCESS(f"Deactivated {deactivated} loop redirect(s)"))
