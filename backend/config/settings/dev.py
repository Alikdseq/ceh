from .base import *  # noqa: F403

DEBUG = True

RUNNING_IN_DOCKER = env.bool("RUNNING_IN_DOCKER", default=False)  # noqa: F405

# Console locally; SMTP in Docker (Mailhog or real SMTP from .env).
_default_email_backend = (
    "django.core.mail.backends.smtp.EmailBackend"
    if RUNNING_IN_DOCKER
    else "django.core.mail.backends.console.EmailBackend"
)
EMAIL_BACKEND = env("EMAIL_BACKEND", default=_default_email_backend)  # noqa: F405

# Send Celery tasks synchronously in dev (emails work without worker)
CELERY_TASK_ALWAYS_EAGER = env.bool("CELERY_TASK_ALWAYS_EAGER", default=True)  # noqa: F405
CELERY_TASK_EAGER_PROPAGATES = True

# Host without Docker: `.env` uses hostname `db` — SQLite + LocMem.
# Docker: persistent SQLite volume + Redis cache from base.py.
_db_url = env("DATABASE_URL", default="")
_use_host_sqlite = "@db:" in _db_url and not RUNNING_IN_DOCKER

if _use_host_sqlite or RUNNING_IN_DOCKER:
    db_name = env("SQLITE_PATH", default=str(BASE_DIR / "db.sqlite3"))  # noqa: F405
    if RUNNING_IN_DOCKER:
        db_name = "/app/db/db.sqlite3"
    DATABASES = {  # noqa: F811
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": db_name,
        }
    }

if _use_host_sqlite:
    CACHES = {  # noqa: F811
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "ekontaktor-dev",
        }
    }

REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"] = [  # noqa: F405
    "rest_framework.renderers.JSONRenderer",
    "rest_framework.renderers.BrowsableAPIRenderer",
]
