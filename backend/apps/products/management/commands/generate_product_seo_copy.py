from django.core.management.base import BaseCommand

from apps.products.models import ProductGroup
from apps.products.seo_templates import apply_product_seo_copy


class Command(BaseCommand):
    help = "Generate meta, h1, full_description HTML and default FAQ for product cards."

    def add_arguments(self, parser):
        parser.add_argument("--overwrite", action="store_true", help="Replace existing SEO fields and FAQ")
        parser.add_argument("--dry-run", action="store_true")
        parser.add_argument("--slug", type=str, help="Single product slug")

    def handle(self, *args, **options):
        qs = ProductGroup.objects.filter(is_active=True).select_related("category")
        if options["slug"]:
            qs = qs.filter(slug=options["slug"])
        updated = 0
        for group in qs:
            if options["dry_run"]:
                updated += 1
                continue
            if apply_product_seo_copy(group, overwrite=options["overwrite"]):
                updated += 1
        self.stdout.write(self.style.SUCCESS(f"Processed {qs.count()} products; updated {updated}"))
