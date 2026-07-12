import os

from django.conf import settings
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand


def clear_axes_lockouts() -> int:
    try:
        from axes.models import AccessAttempt, AccessFailureLog, AccessLog
    except ImportError:
        return 0
    total = (
        AccessAttempt.objects.count()
        + AccessFailureLog.objects.count()
        + AccessLog.objects.count()
    )
    AccessAttempt.objects.all().delete()
    AccessFailureLog.objects.all().delete()
    AccessLog.objects.all().delete()
    return total


class Command(BaseCommand):
    help = "Create or refresh superuser from DJANGO_SUPERUSER_* env vars"

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset-password",
            action="store_true",
            help="Update password from DJANGO_SUPERUSER_PASSWORD even when DEBUG=False",
        )
        parser.add_argument(
            "--unlock",
            action="store_true",
            help="Clear django-axes login lockouts (failed attempt counters)",
        )

    def handle(self, *args, **options):
        username = os.environ.get("DJANGO_SUPERUSER_USERNAME", "admin")
        email = os.environ.get("DJANGO_SUPERUSER_EMAIL", "admin@ekontaktor.ru")
        password = os.environ.get("DJANGO_SUPERUSER_PASSWORD", "")

        if options["unlock"]:
            cleared = clear_axes_lockouts()
            self.stdout.write(self.style.SUCCESS(f"Cleared django-axes records: {cleared}"))

        if not password and not options["unlock"]:
            self.stdout.write("DJANGO_SUPERUSER_PASSWORD not set — skipped user update")
            return

        if not password:
            return

        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                "email": email,
                "is_staff": True,
                "is_superuser": True,
                "is_active": True,
            },
        )

        user.email = email
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True

        should_reset = created or settings.DEBUG or options["reset_password"]
        if should_reset:
            user.set_password(password)
            action = "Created" if created else "Updated password for"
            self.stdout.write(self.style.SUCCESS(f"{action} superuser: {username}"))
        else:
            self.stdout.write(
                f"Superuser {username} exists (use --reset-password to sync password from .env)"
            )

        user.save()

        if settings.DEBUG and not options["unlock"]:
            cleared = clear_axes_lockouts()
            if cleared:
                self.stdout.write(self.style.SUCCESS(f"Cleared django-axes records: {cleared}"))
