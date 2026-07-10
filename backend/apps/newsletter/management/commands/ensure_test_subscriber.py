import os

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.newsletter.models import NewsletterSubscriber


class Command(BaseCommand):
    help = "Ensure test newsletter subscriber is active (dev/UAT)"

    def handle(self, *args, **options):
        email = os.environ.get("TEST_NEWSLETTER_EMAIL", "").strip().lower()
        if not email:
            self.stdout.write("TEST_NEWSLETTER_EMAIL not set — skipped")
            return

        subscriber, created = NewsletterSubscriber.objects.update_or_create(
            email=email,
            defaults={
                "status": NewsletterSubscriber.Status.ACTIVE,
                "confirmed_at": timezone.now(),
            },
        )
        action = "Created" if created else "Updated"
        self.stdout.write(self.style.SUCCESS(f"{action} active subscriber: {email}"))
