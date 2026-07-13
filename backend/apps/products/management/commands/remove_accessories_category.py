from django.core.management.base import BaseCommand

from apps.products.models import Category, ProductGroup
from apps.products.utils import invalidate_catalog_cache

ACCESSORIES_ROOT_SLUG = "aksessuary-kontaktorov"


class Command(BaseCommand):
    help = "Remove accessories category tree and all product cards in it"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show counts without deleting",
        )

    def handle(self, *args, **options):
        root = Category.objects.filter(slug=ACCESSORIES_ROOT_SLUG).first()
        if not root:
            self.stdout.write(self.style.WARNING("Category aksessuary-kontaktorov not found — nothing to do"))
            return

        category_ids = list(root.get_descendants(include_self=True).values_list("pk", flat=True))
        groups_qs = ProductGroup.objects.filter(category_id__in=category_ids)
        group_count = groups_qs.count()
        category_count = len(category_ids)

        self.stdout.write(f"Categories to remove: {category_count}")
        self.stdout.write(f"Product groups to remove: {group_count}")

        if options["dry_run"]:
            self.stdout.write(self.style.WARNING("Dry run — no changes made"))
            return

        deleted_groups, _ = groups_qs.delete()
        root.delete()
        invalidate_catalog_cache()

        self.stdout.write(
            self.style.SUCCESS(
                f"Removed accessories: {category_count} categories, {deleted_groups} related objects"
            )
        )
