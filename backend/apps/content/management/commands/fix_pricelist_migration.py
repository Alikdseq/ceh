"""Fix django_migrations when pricelist tables exist but 0003_pricelist is not recorded."""

from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = "Mark content.0003_pricelist as applied when tables already exist (rename 0002_pricelist if needed)"

    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            tables = connection.introspection.table_names()
            has_section = "content_pricelistsection" in tables
            has_item = "content_pricelistitem" in tables

            cursor.execute(
                "SELECT name FROM django_migrations WHERE app = %s ORDER BY id",
                ["content"],
            )
            applied = {row[0] for row in cursor.fetchall()}

        if "0003_pricelist" in applied:
            self.stdout.write(self.style.SUCCESS("content.0003_pricelist already applied — nothing to do."))
            return

        if not (has_section and has_item):
            self.stdout.write(
                self.style.ERROR(
                    "Pricelist tables missing. Run: python manage.py migrate content"
                )
            )
            return

        if "0002_pricelist" in applied:
            with connection.cursor() as cursor:
                cursor.execute(
                    "UPDATE django_migrations SET name = %s WHERE app = %s AND name = %s",
                    ["0003_pricelist", "content", "0002_pricelist"],
                )
            self.stdout.write(
                self.style.SUCCESS(
                    "Renamed migration record content.0002_pricelist → content.0003_pricelist"
                )
            )
            return

        from django.core.management import call_command

        call_command("migrate", "content", "0003_pricelist", fake=True)
        self.stdout.write(
            self.style.SUCCESS(
                "Tables exist — marked content.0003_pricelist as applied (--fake)."
            )
        )
