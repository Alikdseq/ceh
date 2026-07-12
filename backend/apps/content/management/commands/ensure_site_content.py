import json
from pathlib import Path

from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError

from apps.content.models import Page, PriceListSection

CRITICAL_PAGE_SLUGS = ("about", "contacts", "about-production", "about-certificates", "support")


class Command(BaseCommand):
    help = "Idempotent bootstrap: CMS pages (seed) and public price list table"

    def handle(self, *args, **options):
        self._ensure_cms_pages()
        self._ensure_price_list()

    def _fixture_path(self) -> Path:
        path = Path(__file__).resolve().parents[4] / "fixtures" / "seed_content.json"
        if not path.is_file():
            raise CommandError(f"Fixture not found: {path}")
        return path

    def _ensure_cms_pages(self) -> None:
        missing = [slug for slug in CRITICAL_PAGE_SLUGS if not Page.objects.filter(slug=slug, is_published=True).exists()]
        if not missing:
            self.stdout.write(self.style.SUCCESS("CMS pages OK — nothing to seed"))
            return

        fixture = self._fixture_path()
        if Page.objects.count() == 0:
            call_command("loaddata", str(fixture))
            self.stdout.write(self.style.SUCCESS("Loaded fixtures/seed_content.json"))
            return

        pages_by_slug = self._pages_from_fixture(fixture)
        restored = []
        for slug in missing:
            data = pages_by_slug.get(slug)
            if not data:
                self.stdout.write(self.style.WARNING(f"No fixture data for page slug={slug}"))
                continue
            Page.objects.update_or_create(slug=slug, defaults=data)
            restored.append(slug)

        if restored:
            self.stdout.write(self.style.SUCCESS(f"Restored CMS pages: {', '.join(restored)}"))

    def _pages_from_fixture(self, fixture: Path) -> dict[str, dict]:
        raw = json.loads(fixture.read_text(encoding="utf-8"))
        result: dict[str, dict] = {}
        for entry in raw:
            if entry.get("model") != "content.page":
                continue
            fields = entry["fields"]
            slug = fields["slug"]
            result[slug] = {
                "title": fields["title"],
                "body": fields["body"],
                "meta_title": fields.get("meta_title", ""),
                "meta_description": fields.get("meta_description", ""),
                "h1": fields.get("h1", ""),
                "is_published": fields.get("is_published", True),
                "sort_order": fields.get("sort_order", 0),
            }
        return result

    def _ensure_price_list(self) -> None:
        has_sections = PriceListSection.objects.filter(is_active=True).exists()
        if has_sections:
            self.stdout.write(self.style.SUCCESS("Public price list OK — skipped import"))
            return

        try:
            call_command("import_price_list")
        except CommandError as exc:
            self.stdout.write(self.style.WARNING(f"Public price list import skipped: {exc}"))
            return

        self.stdout.write(self.style.SUCCESS("Imported public price list (content.import_price_list)"))
