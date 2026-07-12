from celery.schedules import crontab

from .base import *  # noqa: F403

DEBUG = False

# SSL завершается на nginx; Django видит HTTP + X-Forwarded-Proto
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True
SECURE_SSL_REDIRECT = env.bool("SECURE_SSL_REDIRECT", default=False)  # noqa: F405
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SAMESITE = "Lax"
# Надёжные сессии админки: Redis + БД (иначе логин может «сбрасываться»)
SESSION_ENGINE = "django.contrib.sessions.backends.cached_db"

# CSRF для POST /manage/login/ за nginx HTTPS
_extra_csrf = ["https://ekontaktor.ru", "https://www.ekontaktor.ru"]
if FRONTEND_URL:  # noqa: F405
    _extra_csrf.append(FRONTEND_URL.rstrip("/"))
CSRF_TRUSTED_ORIGINS = list(dict.fromkeys([*CSRF_TRUSTED_ORIGINS, *_extra_csrf]))  # noqa: F405

# django-axes: реальный IP клиента из nginx
AXES_IPWARE_PROXY_COUNT = 1
AXES_IPWARE_META_PRECEDENCE_ORDER = [
    "HTTP_X_FORWARDED_FOR",
    "X_FORWARDED_FOR",
    "REMOTE_ADDR",
]
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = "DENY"
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"

# Content-Security-Policy set via middleware (apps.core.middleware.SecurityHeadersMiddleware)
CSP_DEFAULT_SRC = ("'self'",)
CSP_SCRIPT_SRC = ("'self'", "'unsafe-inline'", "https://mc.yandex.ru", "https://www.googletagmanager.com")
CSP_IMG_SRC = ("'self'", "data:", "https:", "http:")
CSP_CONNECT_SRC = ("'self'", "https://mc.yandex.ru", "https://www.google-analytics.com")

# Sentry (STEP-111)
SENTRY_DSN = env("SENTRY_DSN", default="")
if SENTRY_DSN:
    import sentry_sdk
    from sentry_sdk.integrations.celery import CeleryIntegration
    from sentry_sdk.integrations.django import DjangoIntegration

    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[DjangoIntegration(), CeleryIntegration()],
        traces_sample_rate=0.1,
        send_default_pii=False,
    )

CELERY_BEAT_SCHEDULE = {
    "generate-sitemap-daily": {
        "task": "apps.seo.tasks.generate_sitemap",
        "schedule": crontab(hour=3, minute=0),
    },
}
