import os

from django.conf import settings
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Create or refresh dev superuser from DJANGO_SUPERUSER_* env vars"

    def handle(self, *args, **options):
        username = os.environ.get("DJANGO_SUPERUSER_USERNAME", "admin")
        email = os.environ.get("DJANGO_SUPERUSER_EMAIL", "admin@ekontaktor.ru")
        password = os.environ.get("DJANGO_SUPERUSER_PASSWORD", "")

        if not password:
            self.stdout.write("DJANGO_SUPERUSER_PASSWORD not set — skipped")
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

        if created or settings.DEBUG:
            user.set_password(password)
            action = "Created" if created else "Updated password for"
            self.stdout.write(self.style.SUCCESS(f"{action} superuser: {username}"))
        else:
            self.stdout.write(f"Superuser {username} already exists")

        user.save()

        if settings.DEBUG:
            try:
                from axes.models import AccessAttempt, AccessFailureLog, AccessLog

                AccessAttempt.objects.all().delete()
                AccessFailureLog.objects.all().delete()
                AccessLog.objects.all().delete()
                self.stdout.write("Cleared login lockouts (django-axes)")
            except ImportError:
                pass
