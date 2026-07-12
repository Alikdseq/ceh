from django.conf import settings


def _admin_path_prefix() -> str:
    admin_url = getattr(settings, "ADMIN_URL", "manage/").strip("/")
    return f"/{admin_url}/"


def _is_admin_request(request) -> bool:
    prefix = _admin_path_prefix()
    path = request.path
    return path.startswith(prefix) or path == prefix.rstrip("/")


def _build_csp(*, allow_unsafe_eval: bool) -> str:
    script_src = ["'self'", "'unsafe-inline'"]
    if allow_unsafe_eval:
        script_src.append("'unsafe-eval'")
    script_src.extend(["https://mc.yandex.ru", "https://www.googletagmanager.com"])
    return (
        "default-src 'self'; "
        f"script-src {' '.join(script_src)}; "
        "img-src 'self' data: https: http:; "
        "connect-src 'self' https://mc.yandex.ru https://www.google-analytics.com; "
        "frame-src https://yandex.ru https://*.yandex.ru; "
        "style-src 'self' 'unsafe-inline'; "
        "font-src 'self' data:"
    )


class SecurityHeadersMiddleware:
    """CSP and security headers for production (STEP-105)."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if not getattr(settings, "DEBUG", True):
            allow_eval = _is_admin_request(request)
            response["Content-Security-Policy"] = _build_csp(allow_unsafe_eval=allow_eval)
            response["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        return response
