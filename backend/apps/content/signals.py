from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import NewsPost
from .tasks import send_news_post_task


@receiver(post_save, sender=NewsPost)
def queue_news_post_newsletter(sender, instance: NewsPost, **kwargs):
    if not instance.is_published:
        return
    if NewsPost.objects.filter(pk=instance.pk, newsletter_sent_at__isnull=False).exists():
        return
    send_news_post_task.delay(instance.pk)
