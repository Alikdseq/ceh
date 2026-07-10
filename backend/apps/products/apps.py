from django.apps import AppConfig


class ProductsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.products"
    verbose_name = "Каталог"

    def ready(self):
        from apps.core.audit import register_auditlog
        import apps.products.signals  # noqa: F401

        register_auditlog()
