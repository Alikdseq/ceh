from pathlib import Path

import yaml
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.core.paths import resolve_data_file
from apps.products.models import Category


class Command(BaseCommand):
    help = "Import category tree from YAML (STEP-031)"

    def add_arguments(self, parser):
        parser.add_argument(
            "yaml_path",
            nargs="?",
            default="categories.yaml",
            type=str,
            help="Path to categories.yaml (host data/ or /data/ in Docker)",
        )
        parser.add_argument("--clear", action="store_true", help="Delete existing categories first")

    @transaction.atomic
    def handle(self, *args, **options):
        path = resolve_data_file(options["yaml_path"], default_name="categories.yaml")
        if not path.is_file():
            raise CommandError(
                f"File not found: {options['yaml_path']} "
                f"(also checked /data/categories.yaml on the host mount)"
            )

        if options["clear"]:
            Category.objects.all().delete()
            self.stdout.write("Cleared existing categories")

        with path.open(encoding="utf-8") as f:
            data = yaml.safe_load(f)

        created = 0
        for node in data.get("categories", []):
            created += self._create_node(node, parent=None)

        roots = Category.objects.filter(parent__isnull=True).count()
        total = Category.objects.count()
        self.stdout.write(self.style.SUCCESS(
            f"Done: {created} nodes processed, {roots} root categories, {total} total"
        ))

    def _create_node(self, node: dict, parent: Category | None) -> int:
        count = 1
        cat, was_created = Category.objects.update_or_create(
            slug=node["slug"],
            defaults={
                "name": node["name"],
                "parent": parent,
                "description": node.get("description", ""),
                "meta_title": node.get("meta_title", ""),
                "meta_description": node.get("meta_description", ""),
                "h1": node.get("h1", node["name"]),
                "sort_order": node.get("sort_order", 0),
                "is_active": True,
            },
        )
        action = "Created" if was_created else "Updated"
        self.stdout.write(f"  {action}: {cat.name} ({cat.slug})")

        for child in node.get("children", []):
            count += self._create_node(child, parent=cat)
        return count
