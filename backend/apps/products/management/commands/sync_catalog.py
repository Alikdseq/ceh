from pathlib import Path

from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Full catalog sync: text catalog import + pricelist + optional prune"

    def add_arguments(self, parser):
        parser.add_argument(
            "--text-path",
            default="тексткаталога.txt",
            help="Path to тексткаталога.txt",
        )
        parser.add_argument(
            "--pricelist",
            default="data/pricelist.csv",
            help="Path to pricelist CSV",
        )
        parser.add_argument(
            "--prune",
            action="store_true",
            help="Deactivate KT/KTP/KTE items missing from text catalog",
        )
        parser.add_argument(
            "--skip-pricelist",
            action="store_true",
            help="Skip pricelist import",
        )

    def handle(self, *args, **options):
        repo_root = Path(__file__).resolve().parents[5]
        text_path = self._resolve_path(options["text_path"], repo_root / "тексткаталога.txt")
        pricelist_path = self._resolve_path(options["pricelist"], repo_root / "data" / "pricelist.csv")

        self.stdout.write("Step 1/2: import catalog text…")
        cmd_args = [str(text_path)]
        if options["prune"]:
            cmd_args.append("--prune")
        call_command("import_catalog_text", *cmd_args)

        if not options["skip_pricelist"]:
            if not pricelist_path.exists():
                raise CommandError(f"Pricelist not found: {pricelist_path}")
            self.stdout.write("Step 2/2: import pricelist…")
            call_command("import_pricelist", str(pricelist_path))

        self.stdout.write(self.style.SUCCESS("Catalog sync complete."))

    def _resolve_path(self, raw: str, fallback: Path) -> Path:
        from apps.core.paths import resolve_data_file

        path = resolve_data_file(raw, default_name=fallback.name)
        if path.is_file():
            return path
        if fallback.exists():
            return fallback
        repo_root = Path(__file__).resolve().parents[5]
        candidate = repo_root / raw
        if candidate.exists():
            return candidate
        return path
