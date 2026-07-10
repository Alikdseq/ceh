from django.core.management.base import BaseCommand

from apps.seo.services.sitemap import write_sitemap_file


class Command(BaseCommand):
    help = "Generate sitemap.xml (STEP-101)"

    def handle(self, *args, **options):
        path = write_sitemap_file()
        self.stdout.write(self.style.SUCCESS(f"Sitemap written: {path}"))
