from django.conf import settings


class SecurityHeadersMiddleware:
    """CSP and security headers for production (STEP-105)."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if not getattr(settings, "DEBUG", True):
            response["Content-Security-Policy"] = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' https://mc.yandex.ru https://www.googletagmanager.com; "
                "img-src 'self' data: https: http:; "
                "connect-src 'self' https://mc.yandex.ru https://www.google-analytics.com; "
                "frame-src https://yandex.ru https://*.yandex.ru; "
                "style-src 'self' 'unsafe-inline'"
            )
            response["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        return response
