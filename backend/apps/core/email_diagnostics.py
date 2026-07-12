"""SMTP error hints for production diagnostics."""

from __future__ import annotations

import smtplib


def smtp_error_hint(exc: BaseException) -> str:
    message = str(exc).lower()
    lines: list[str] = []

    if isinstance(exc, smtplib.SMTPAuthenticationError) or "authentication failed" in message:
        lines.append("Яндекс отклонил логин SMTP (код 535).")
        lines.append("")
        lines.append("Проверьте по шагам:")
        lines.append("1. Войдите на https://mail.yandex.ru под тем же ящиком, что в EMAIL_HOST_USER.")
        lines.append("2. Настройки → Почтовые программы → включите «С сервера imap.yandex.ru» (IMAP/SMTP).")
        lines.append("3. https://id.yandex.ru/security → включите двухфакторную аутентификацию.")
        lines.append("4. Там же → Пароли приложений → создайте пароль для «Почта».")
        lines.append("5. В .env укажите EMAIL_HOST_PASSWORD=этот пароль (не обычный пароль от ящика).")
        lines.append("6. DEFAULT_FROM_EMAIL должен совпадать с EMAIL_HOST_USER.")
        lines.append("")
        lines.append("Альтернатива: почта домена на Beget (smtp.beget.com:465, SSL).")

    if "timed out" in message or "timeout" in message:
        lines.append("Таймаут SMTP. Проверьте EMAIL_PORT, EMAIL_USE_TLS/EMAIL_USE_SSL и фаервол VPS.")

    if "connection refused" in message:
        lines.append("Сервер SMTP недоступен. Проверьте EMAIL_HOST и порт.")

    return "\n".join(lines)
