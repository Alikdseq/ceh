from auditlog.registry import auditlog

from apps.content.models import SiteSettings
from apps.products.models import ProductGroup, ProductVariant
from apps.quotes.models import QuoteRequest


def register_auditlog():
    auditlog.register(ProductGroup)
    auditlog.register(ProductVariant)
    auditlog.register(QuoteRequest)
    auditlog.register(SiteSettings)
