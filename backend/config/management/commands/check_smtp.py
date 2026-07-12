import smtplib
import socket

from django.conf import settings
from django.core.mail import EmailMessage
from django.core.management.base import BaseCommand, CommandError

from apps.core.email_diagnostics import smtp_error_hint


class Command(BaseCommand):
    help = "Check SMTP settings and authentication (diagnose email delivery)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--send",
            action="store_true",
            help="Also send a test message after successful auth",
        )
        parser.add_argument("--to", default="", help="Recipient for --send")

    def handle(self, *args, **options):
        user = settings.EMAIL_HOST_USER
        password = settings.EMAIL_HOST_PASSWORD
        host = settings.EMAIL_HOST
        port = settings.EMAIL_PORT

        self.stdout.write("=== SMTP configuration ===")
        self.stdout.write(f"  HOST:     {host}")
        self.stdout.write(f"  PORT:     {port}")
        self.stdout.write(f"  TLS:      {settings.EMAIL_USE_TLS}")
        self.stdout.write(f"  SSL:      {settings.EMAIL_USE_SSL}")
        self.stdout.write(f"  TIMEOUT:  {settings.EMAIL_TIMEOUT}s")
        self.stdout.write(f"  USER:     {user or '(empty)'}")
        self.stdout.write(f"  PASSWORD: {'set (' + str(len(password)) + ' chars)' if password else '(empty)'}")
        self.stdout.write(f"  FROM:     {settings.DEFAULT_FROM_EMAIL}")

        if not user or not password:
            raise CommandError("EMAIL_HOST_USER и EMAIL_HOST_PASSWORD должны быть заданы в .env")

        if user != settings.DEFAULT_FROM_EMAIL:
            self.stdout.write(
                self.style.WARNING(
                    "  WARNING: DEFAULT_FROM_EMAIL != EMAIL_HOST_USER — Яндекс может отклонять письма"
                )
            )

        self.stdout.write("\n=== TCP connection ===")
        try:
            with socket.create_connection((host, port), timeout=settings.EMAIL_TIMEOUT):
                self.stdout.write(self.style.SUCCESS(f"  OK: {host}:{port} reachable"))
        except OSError as exc:
            raise CommandError(f"TCP failed: {exc}") from exc

        self.stdout.write("\n=== SMTP login ===")
        try:
            if settings.EMAIL_USE_SSL:
                client = smtplib.SMTP_SSL(host, port, timeout=settings.EMAIL_TIMEOUT)
            else:
                client = smtplib.SMTP(host, port, timeout=settings.EMAIL_TIMEOUT)
                if settings.EMAIL_USE_TLS:
                    client.starttls()
            client.login(user, password)
            client.quit()
            self.stdout.write(self.style.SUCCESS("  OK: authentication successful"))
        except smtplib.SMTPException as exc:
            hint = smtp_error_hint(exc)
            raise CommandError(f"SMTP auth failed: {exc}\n\n{hint}") from exc

        if options["send"]:
            to = (options["to"] or "").strip()
            if not to:
                from apps.quotes.services.quotes import get_order_recipients

                recipients = get_order_recipients()
                if not recipients:
                    raise CommandError("No recipients for --send")
                to = recipients[0]

            msg = EmailMessage(
                subject="Тест SMTP — Электроконтактор",
                body="Тестовое письмо. SMTP работает.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[to],
            )
            try:
                msg.send(fail_silently=False)
            except Exception as exc:
                hint = smtp_error_hint(exc)
                raise CommandError(f"Send failed: {exc}\n\n{hint}") from exc
            self.stdout.write(self.style.SUCCESS(f"\nTest email sent to {to}"))
