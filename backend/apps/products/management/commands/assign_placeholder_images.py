import shutil
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from apps.products.models import ProductGroup, ProductImage
from apps.products.product_media import image_file_exists

PLACEHOLDER_NAME = "placeholder-product.svg"


class Command(BaseCommand):
    help = "Assign placeholder image to product groups without images (STEP-034)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--source",
            type=str,
            default="",
            help="Path to placeholder SVG (default: frontend/public/placeholder-product.svg)",
        )

    def handle(self, *args, **options):
        repo_root = Path(settings.BASE_DIR).parent
        source = Path(options["source"]) if options["source"] else repo_root / "frontend" / "public" / PLACEHOLDER_NAME

        if not source.exists():
            self.stdout.write(self.style.WARNING(f"Placeholder not found: {source}"))
            return

        dest_dir = Path(settings.MEDIA_ROOT) / "products"
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest = dest_dir / PLACEHOLDER_NAME
        shutil.copy2(source, dest)

        media_path = f"products/{PLACEHOLDER_NAME}"
        assigned = 0

        for group in ProductGroup.objects.filter(is_active=True):
            has_valid = any(
                image_file_exists(img.image)
                for img in group.images.all()
            )
            if has_valid:
                continue
            ProductImage.objects.create(
                group=group,
                image=media_path,
                alt=group.name,
                sort_order=0,
                is_primary=True,
            )
            assigned += 1

        self.stdout.write(self.style.SUCCESS(
            f"Placeholder assigned to {assigned} groups ({ProductImage.objects.count()} total images)"
        ))
