from django.conf import settings


def _admin_path_prefix() -> str:
    admin_url = (getattr(settings, "ADMIN_URL", "manage/") or "manage/").strip("/")
    if not admin_url:
        admin_url = "manage"
    return f"/{admin_url}/"


def _is_admin_request(request) -> bool:
    prefix = _admin_path_prefix()
    path = request.path
    return path.startswith(prefix) or path == prefix.rstrip("/")


def _build_csp(*, allow_unsafe_eval: bool) -> str:
    script_src = ["'self'", "'unsafe-inline'"]
    if allow_unsafe_eval:
        script_src.extend(["'unsafe-eval'", "blob:"])
    script_src.extend(["https://mc.yandex.ru", "https://www.googletagmanager.com"])
    connect_src = ["'self'", "https://mc.yandex.ru", "https://www.google-analytics.com"]
    if allow_unsafe_eval:
        connect_src.append("blob:")
    return (
        "default-src 'self'; "
        f"script-src {' '.join(script_src)}; "
        "img-src 'self' data: https: http: blob:; "
        f"connect-src {' '.join(connect_src)}; "
        "frame-src https://yandex.ru https://*.yandex.ru; "
        "style-src 'self' 'unsafe-inline'; "
        "font-src 'self' data:; "
        "worker-src 'self' blob:"
    )


class SecurityHeadersMiddleware:
    """CSP and security headers for production (STEP-105)."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if getattr(settings, "DEBUG", True):
            return response
        if _is_admin_request(request):
            # Django admin / Unfold JS (inlines, filters) requires unsafe-eval.
            response["Content-Security-Policy"] = _build_csp(allow_unsafe_eval=True)
            return response
        response["Content-Security-Policy"] = _build_csp(allow_unsafe_eval=False)
        response["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        return response
