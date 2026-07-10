from django.template.loader import render_to_string

from apps.content.models import NewsPost
from apps.newsletter.serializers import get_site_url


def news_post_url(news: NewsPost) -> str:
    return f"{get_site_url()}/news/{news.slug}/"


def render_news_post_email(news: NewsPost, subscriber) -> str:
    unsubscribe_url = f"{get_site_url()}/unsubscribe/{subscriber.unsubscribe_token}"
    return render_to_string("newsletter/news_post_email.html", {
        "news": news,
        "subscriber": subscriber,
        "news_url": news_post_url(news),
        "unsubscribe_url": unsubscribe_url,
    })
