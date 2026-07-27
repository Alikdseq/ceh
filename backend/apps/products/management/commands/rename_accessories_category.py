"""Rename «Аксессуары» category and pricelist section to «Комплектующие»."""

from django.core.management.base import BaseCommand
from django.db.models import Q

from apps.content.models import PriceListSection
from apps.content.services.pricelist import merge_duplicate_pricelist_sections
from apps.products.models import Category
from apps.products.utils import invalidate_catalog_cache

ACCESSORIES_ROOT_SLUG = "aksessuary-kontaktorov"


class Command(BaseCommand):
    help = "Rename accessories category/sections to Комплектующие (slug unchanged)"

    def handle(self, *args, **options):
        root = Category.objects.filter(slug=ACCESSORIES_ROOT_SLUG).first()
        if root and root.name != "Комплектующие":
            old = root.name
            root.name = "Комплектующие"
            root.save(update_fields=["name"])
            self.stdout.write(f"Category: {old!r} → Комплектующие")

        renamed_cats = Category.objects.filter(
            Q(name__icontains="аксессуар") & ~Q(slug=ACCESSORIES_ROOT_SLUG)
        ).update(name="Комплектующие")
        if renamed_cats:
            self.stdout.write(f"Renamed {renamed_cats} related categories")

        for old_name in ("Аксессуары", "Аксессуары к контакторам"):
            section = PriceListSection.objects.filter(name=old_name).first()
            if section:
                section.name = "Комплектующие"
                section.save(update_fields=["name"])
                self.stdout.write(f"Price list section: {old_name} → Комплектующие")

        merged = merge_duplicate_pricelist_sections()
        if merged:
            self.stdout.write(f"Merged {merged} duplicate «Комплектующие» section(s)")

        invalidate_catalog_cache()
        self.stdout.write(self.style.SUCCESS("Accessories renamed to Комплектующие"))
