from django.core.management.base import BaseCommand

from apps.products.models import Category, ProductGroup
from apps.products.utils import invalidate_catalog_cache

POWER_SWITCHES_SLUG = "vyklyuchateli-silovye"


class Command(BaseCommand):
    help = "Remove empty «Выключатели силовые» subcategory under ВПК"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show counts without deleting",
        )

    def handle(self, *args, **options):
        category = Category.objects.filter(slug=POWER_SWITCHES_SLUG).first()
        if not category:
            self.stdout.write(
                self.style.WARNING(f"Category {POWER_SWITCHES_SLUG} not found — nothing to do")
            )
            return

        group_count = ProductGroup.objects.filter(category=category).count()
        self.stdout.write(f"Category: {category.name} ({category.slug})")
        self.stdout.write(f"Product groups in category: {group_count}")

        if options["dry_run"]:
            self.stdout.write(self.style.WARNING("Dry run — no changes made"))
            return

        if group_count:
            self.stderr.write(
                self.style.ERROR(
                    f"Refusing to delete: {group_count} product(s) still assigned. Move them first."
                )
            )
            return

        category.delete()
        invalidate_catalog_cache()
        self.stdout.write(self.style.SUCCESS(f"Removed category {POWER_SWITCHES_SLUG}"))
