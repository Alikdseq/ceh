from django.core.management.base import BaseCommand

from apps.products.models import Category, ProductGroup
from apps.products.seo_templates import apply_category_meta, apply_product_meta


class Command(BaseCommand):
    help = "Generate fallback meta_title/meta_description for categories and products."

    def add_arguments(self, parser):
        parser.add_argument("--categories", action="store_true", help="Process categories")
        parser.add_argument("--products", action="store_true", help="Process product groups")
        parser.add_argument("--overwrite", action="store_true", help="Overwrite existing meta fields")
        parser.add_argument("--dry-run", action="store_true", help="Show counts without saving")

    def handle(self, *args, **options):
        do_categories = options["categories"] or not (options["categories"] or options["products"])
        do_products = options["products"] or not (options["categories"] or options["products"])
        overwrite = options["overwrite"]
        dry_run = options["dry_run"]

        cat_updated = 0
        prod_updated = 0

        if do_categories:
            for category in Category.objects.filter(is_active=True):
                if dry_run:
                    if overwrite or not category.meta_title or not category.meta_description:
                        cat_updated += 1
                elif apply_category_meta(category, overwrite=overwrite):
                    cat_updated += 1

        if do_products:
            for group in ProductGroup.objects.filter(is_active=True).select_related("category"):
                if dry_run:
                    if overwrite or not group.meta_title or not group.meta_description:
                        prod_updated += 1
                elif apply_product_meta(group, overwrite=overwrite):
                    prod_updated += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"{'Would update' if dry_run else 'Updated'}: "
                f"{cat_updated} categories, {prod_updated} products"
            )
        )
