from django.core.management.base import BaseCommand

from apps.seo.services.indexnow import submit_indexnow_urls
from apps.seo.tasks import submit_indexnow


class Command(BaseCommand):
    help = "Submit URLs to IndexNow (Yandex, Bing)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--url",
            action="append",
            dest="urls",
            help="Relative or absolute URL to submit (repeatable)",
        )
        parser.add_argument(
            "--async",
            action="store_true",
            dest="use_async",
            help="Queue Celery task instead of synchronous submit",
        )

    def handle(self, *args, **options):
        urls = options.get("urls") or ["/"]
        if options.get("use_async"):
            submit_indexnow.delay(urls)
            self.stdout.write(self.style.SUCCESS(f"Queued IndexNow for {len(urls)} URL(s)"))
            return

        result = submit_indexnow_urls(urls)
        self.stdout.write(str(result))
