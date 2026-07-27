"""Merge duplicate PriceListSection rows with the same name."""

from django.core.management.base import BaseCommand

from apps.content.services.pricelist import merge_duplicate_pricelist_sections


class Command(BaseCommand):
    help = "Merge duplicate pricelist sections (e.g. two «Комплектующие» blocks)"

    def handle(self, *args, **options):
        merged = merge_duplicate_pricelist_sections()
        if merged:
            self.stdout.write(self.style.SUCCESS(f"Merged {merged} duplicate section(s)"))
        else:
            self.stdout.write(self.style.SUCCESS("No duplicate pricelist sections found"))
