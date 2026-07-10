from django.core.management.base import BaseCommand
from django.db import connection

from apps.products.services.search import rebuild_all_search_indexes


class Command(BaseCommand):
    help = "Rebuild search_vector fields and verify pg_trgm (STEP-035)"

    def handle(self, *args, **options):
        if connection.vendor == "postgresql":
            with connection.cursor() as cursor:
                cursor.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")

        groups, variants = rebuild_all_search_indexes()
        self.stdout.write(self.style.SUCCESS(
            f"Search index rebuilt: {groups} groups, {variants} variants updated"
        ))
