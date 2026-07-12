import pytest
import smtplib

from apps.core.email_diagnostics import smtp_error_hint


def test_smtp_auth_error_hint():
    exc = smtplib.SMTPAuthenticationError(535, b"authentication failed")
    hint = smtp_error_hint(exc)
    assert "535" in hint or "Пароли приложений" in hint
    assert "DEFAULT_FROM_EMAIL" in hint
