from django.conf import settings
from django.core.mail import EmailMessage
from django.core.management.base import BaseCommand, CommandError

from apps.core.email_diagnostics import smtp_error_hint


class Command(BaseCommand):
    help = "Send a test email synchronously (diagnose SMTP without Celery)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--to",
            default="",
            help="Recipient email (default: first ORDER_EMAILS / SiteSettings order email)",
        )

    def handle(self, *args, **options):
        to = (options["to"] or "").strip()
        if not to:
            from apps.quotes.services.quotes import get_order_recipients

            recipients = get_order_recipients()
            if not recipients:
                raise CommandError("No recipients. Set ORDER_EMAILS or SiteSettings.order_emails")
            to = recipients[0]

        if not settings.EMAIL_HOST_USER or not settings.EMAIL_HOST_PASSWORD:
            raise CommandError("EMAIL_HOST_USER and EMAIL_HOST_PASSWORD must be set in .env")

        self.stdout.write(
            f"SMTP: {settings.EMAIL_HOST}:{settings.EMAIL_PORT} "
            f"TLS={settings.EMAIL_USE_TLS} SSL={settings.EMAIL_USE_SSL} "
            f"timeout={settings.EMAIL_TIMEOUT}s"
        )
        self.stdout.write(f"From: {settings.DEFAULT_FROM_EMAIL} → To: {to}")

        msg = EmailMessage(
            subject="Тест SMTP — Электроконтактор",
            body=(
                "Тестовое письмо с сервера ekontaktor.ru.\n"
                "Если вы видите это письмо — SMTP настроен корректно.\n"
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[to],
        )
        try:
            sent = msg.send(fail_silently=False)
        except Exception as exc:
            hint = smtp_error_hint(exc)
            raise CommandError(f"SMTP failed: {exc}\n\n{hint}") from exc

        self.stdout.write(self.style.SUCCESS(f"Sent ({sent} message). Check inbox and spam for {to}"))
