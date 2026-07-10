import os
from pathlib import Path

import environ

env = environ.Env(
    DEBUG=(bool, False),
    ALLOWED_HOSTS=(list, ["localhost", "127.0.0.1"]),
)

BASE_DIR = Path(__file__).resolve().parent.parent.parent

environ.Env.read_env(BASE_DIR.parent / ".env")

SECRET_KEY = env("SECRET_KEY", default="dev-insecure-change-me")
DEBUG = env.bool("DEBUG", default=False)
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["localhost", "127.0.0.1", "backend"])

INSTALLED_APPS = [
    "unfold",
    "unfold.contrib.filters",
    "unfold.contrib.forms",
    "unfold.contrib.import_export",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.postgres",
    # Third party
    "rest_framework",
    "corsheaders",
    "django_filters",
    "drf_spectacular",
    "mptt",
    "import_export",
    "axes",
    "django_otp",
    "django_otp.plugins.otp_totp",
    "auditlog",
    "django_celery_beat",
    # Local apps
    "apps.users",
    "apps.products",
    "apps.docs",
    "apps.quotes",
    "apps.content",
    "apps.newsletter",
    "apps.leads",
    "apps.seo",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django_otp.middleware.OTPMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "axes.middleware.AxesMiddleware",
    "auditlog.middleware.AuditlogMiddleware",
    "apps.core.middleware.SecurityHeadersMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

DATABASES = {
    "default": env.db("DATABASE_URL", default="postgres://ekontaktor:ekontaktor@localhost:5432/ekontaktor")
}

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": env("REDIS_URL", default="redis://127.0.0.1:6379/0"),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "SOCKET_CONNECT_TIMEOUT": 5,
            "SOCKET_TIMEOUT": 5,
        },
        "KEY_PREFIX": "ek",
    }
}

# Cache TTLs (TZ §9.2, STEP-107)
CACHE_TTL_CATEGORIES = 3600
CACHE_TTL_SEARCH_SUGGEST = 300
CACHE_TTL_PRODUCT_DETAIL = 600
CACHE_TTL_PAGE = 1800

SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

AUTHENTICATION_BACKENDS = [
    "axes.backends.AxesStandaloneBackend",
    "django.contrib.auth.backends.ModelBackend",
]

LANGUAGE_CODE = "ru-ru"
TIME_ZONE = "Europe/Moscow"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# DRF — public B2B API uses X-Cart-Session, not Django session auth (avoids CSRF on cart POST).
REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_AUTHENTICATION_CLASSES": [],
    "DEFAULT_PERMISSION_CLASSES": [],
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 24,
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
    ],
    "DEFAULT_PARSER_CLASSES": [
        "rest_framework.parsers.JSONParser",
        "rest_framework.parsers.FormParser",
    ],
}

SPECTACULAR_SETTINGS = {
    "TITLE": "Электроконтактор API",
    "DESCRIPTION": "B2B каталог и заявки",
    "VERSION": "1.0.0",
}

CORS_ALLOWED_ORIGINS = env.list(
    "CORS_ALLOWED_ORIGINS",
    default=["http://localhost:3000", "http://127.0.0.1:3000"],
)
CORS_ALLOW_CREDENTIALS = True

CSRF_TRUSTED_ORIGINS = env.list(
    "CSRF_TRUSTED_ORIGINS",
    default=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ],
)

# Admin
ADMIN_URL = env("ADMIN_URL", default="manage/")

# Email
EMAIL_BACKEND = env("EMAIL_BACKEND", default="django.core.mail.backends.smtp.EmailBackend")
EMAIL_HOST = env("EMAIL_HOST", default="localhost")
EMAIL_PORT = env.int("EMAIL_PORT", default=587)
EMAIL_HOST_USER = env("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD", default="")
EMAIL_USE_TLS = env.bool("EMAIL_USE_TLS", default=True)
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", default="noreply@ekontaktor.ru")
ORDER_EMAILS = env.list("ORDER_EMAILS", default=["info@ekontaktor.ru"])

# Celery
CELERY_BROKER_URL = env("REDIS_URL", default="redis://127.0.0.1:6379/0")
CELERY_RESULT_BACKEND = env("REDIS_URL", default="redis://127.0.0.1:6379/0")
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = TIME_ZONE

# Axes
AXES_FAILURE_LIMIT = 5
AXES_COOLOFF_TIME = 0.5  # hours
AXES_LOCKOUT_PARAMETERS = ["ip_address"]

# Auditlog
AUDITLOG_INCLUDE_ALL_MODELS = False

# Upload limits
DATA_UPLOAD_MAX_MEMORY_SIZE = 20 * 1024 * 1024
FILE_UPLOAD_MAX_MEMORY_SIZE = 20 * 1024 * 1024

ALLOWED_UPLOAD_MIME_TYPES = [
    "application/pdf",
    "image/jpeg",
    "image/png",
    "image/webp",
    "application/acad",
    "application/octet-stream",
    "application/x-dwg",
]

CRM_WEBHOOK_URL = env("CRM_WEBHOOK_URL", default="")
FRONTEND_URL = env("FRONTEND_URL", default="http://localhost:3000")

INDEXNOW_KEY = env("INDEXNOW_KEY", default="")
INDEXNOW_ENABLED = env.bool("INDEXNOW_ENABLED", default=False)

UNFOLD = {
    "SITE_TITLE": "Электроконтактор",
    "SITE_HEADER": "Управление сайтом",
    "SITE_SUBHEADER": "Каталог, заявки, прайс и новости",
    "SITE_SYMBOL": "dashboard",
    "SHOW_HISTORY": False,
    "SHOW_VIEW_ON_SITE": True,
    "DASHBOARD_CALLBACK": "config.admin_dashboard.dashboard_callback",
    "COLORS": {
        "primary": {
            "50": "#e5f1f8",
            "100": "#cce3f1",
            "200": "#99c7e3",
            "300": "#66abd5",
            "400": "#338fc7",
            "500": "#0077af",
            "600": "#005684",
            "700": "#003456",
            "800": "#002840",
            "900": "#001a2b",
            "950": "#000d15",
        },
    },
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": False,
        "navigation": [
            {
                "title": "Главная",
                "separator": True,
                "items": [
                    {
                        "title": "Обзор",
                        "icon": "dashboard",
                        "link": "/manage/",
                    },
                ],
            },
            {
                "title": "Каталог",
                "separator": True,
                "items": [
                    {
                        "title": "Карточки товаров",
                        "icon": "inventory_2",
                        "link": "/manage/products/productgroup/",
                    },
                    {
                        "title": "Категории",
                        "icon": "category",
                        "link": "/manage/products/category/",
                    },
                ],
            },
            {
                "title": "Прайс-лист",
                "separator": True,
                "items": [
                    {
                        "title": "Разделы прайса",
                        "icon": "table_chart",
                        "link": "/manage/content/pricelistsection/",
                    },
                ],
            },
            {
                "title": "Заявки",
                "separator": True,
                "items": [
                    {
                        "title": "Заявки с сайта",
                        "icon": "inbox",
                        "link": "/manage/quotes/quoterequest/",
                    },
                ],
            },
            {
                "title": "Контент",
                "separator": True,
                "items": [
                    {
                        "title": "Новости",
                        "icon": "newspaper",
                        "link": "/manage/content/newspost/",
                    },
                ],
            },
        ],
    },
}
