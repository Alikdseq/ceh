"""Detect redirect loops in DB Redirect rows and legacy_site.yaml."""

from django.core.management.base import BaseCommand

from apps.seo.models import Redirect
from apps.seo.services.legacy_paths import collect_legacy_redirect_pairs, paths_equivalent
from apps.seo.services.redirect_resolve import resolve_redirect


class Command(BaseCommand):
    help = "Report self-referential redirects and multi-hop loops (DB + legacy yaml)"

    def add_arguments(self, parser):
        parser.add_argument("--fail-on-error", action="store_true")

    def handle(self, *args, **options):
        issues: list[str] = []

        for redirect in Redirect.objects.filter(is_active=True).iterator():
            if paths_equivalent(redirect.old_path, redirect.new_path):
                issues.append(f"DB loop: {redirect.old_path} → {redirect.new_path}")

        for old_path, new_path in collect_legacy_redirect_pairs():
            if paths_equivalent(old_path, new_path):
                issues.append(f"Legacy yaml loop: {old_path} → {new_path}")

        for redirect in Redirect.objects.filter(is_active=True).iterator():
            chain = self._follow_chain(redirect.old_path, max_hops=10)
            if chain and chain[-1] == chain[0]:
                issues.append(f"Multi-hop loop: {' → '.join(chain)}")

        if issues:
            self.stdout.write(self.style.WARNING(f"Found {len(issues)} redirect loop(s):"))
            for line in issues:
                self.stdout.write(f"  - {line}")
        else:
            self.stdout.write(self.style.SUCCESS("No redirect loops detected"))

        if options["fail_on_error"] and issues:
            raise SystemExit(1)

    def _follow_chain(self, start: str, max_hops: int) -> list[str] | None:
        chain = [start.rstrip("/")]
        current = start
        for _ in range(max_hops):
            target = resolve_redirect(current)
            if not target:
                return None
            norm = target.rstrip("/")
            if norm in chain:
                chain.append(norm)
                return chain
            chain.append(norm)
            current = target
        return None
