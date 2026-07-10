from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from mptt.signals import node_moved

from .models import Category, ProductGroup
from .utils import invalidate_catalog_cache


@receiver([post_save, post_delete], sender=Category)
def invalidate_categories_cache(sender, **kwargs):
    invalidate_catalog_cache()


@receiver(node_moved, sender=Category)
def invalidate_categories_cache_on_move(sender, **kwargs):
    invalidate_catalog_cache()


@receiver([post_save, post_delete], sender=ProductGroup)
def invalidate_products_cache(sender, **kwargs):
    invalidate_catalog_cache()
