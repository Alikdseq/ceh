"""Sync variant prices from pricelist base SKUs to coil/aux siblings."""

from django.core.management.base import BaseCommand

from apps.products.models import ProductVariant
from apps.products.services.pricing import sync_all_variant_prices


class Command(BaseCommand):
    help = "Propagate existing variant prices to siblings (coil voltage, aux contacts)"

    def handle(self, *args, **options):
        stats = sync_all_variant_prices()
        zero_price = ProductVariant.objects.filter(is_active=True, price=0).count()
        self.stdout.write(
            self.style.SUCCESS(
                f"Synced {stats['within_group']} within group, "
                f"{stats['by_sku_prefix']} by SKU prefix; "
                f"{zero_price} active variant(s) still without price"
            )
        )
