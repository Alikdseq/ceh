"""Hide models that are not needed in the simplified CMS admin."""

from django.contrib import admin


def _unregister(model):
    try:
        admin.site.unregister(model)
    except admin.sites.NotRegistered:
        pass


def hide_unneeded_admin_models():
    from django.contrib.auth.models import Group, User
    from django_otp.plugins.otp_totp.models import TOTPDevice

    from apps.content.models import FAQItem, Page, PriceListItem, SiteSettings
    from apps.docs.models import Document, ProductDocument
    from apps.leads.models import CallbackLead, ContactLead, DocumentRequestLead
    from apps.newsletter.models import NewsletterCampaign, NewsletterSendLog, NewsletterSubscriber
    from apps.quotes.models import QuoteCart
    from apps.seo.models import Redirect, SearchQueryLog

    for model in (
        QuoteCart,
        Page,
        FAQItem,
        SiteSettings,
        PriceListItem,
        ContactLead,
        CallbackLead,
        DocumentRequestLead,
        NewsletterSubscriber,
        NewsletterCampaign,
        NewsletterSendLog,
        Redirect,
        SearchQueryLog,
        Document,
        ProductDocument,
        User,
        Group,
        TOTPDevice,
    ):
        _unregister(model)

    try:
        from auditlog.models import LogEntry

        _unregister(LogEntry)
    except ImportError:
        pass

    try:
        from django_celery_beat.models import (
            ClockedSchedule,
            CrontabSchedule,
            IntervalSchedule,
            PeriodicTask,
            SolarSchedule,
        )

        for model in (
            PeriodicTask,
            IntervalSchedule,
            CrontabSchedule,
            SolarSchedule,
            ClockedSchedule,
        ):
            _unregister(model)
    except ImportError:
        pass

    try:
        from axes.models import AccessAttempt, AccessFailureLog, AccessLog

        for model in (AccessAttempt, AccessFailureLog, AccessLog):
            _unregister(model)
    except ImportError:
        pass
