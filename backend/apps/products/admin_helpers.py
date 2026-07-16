"""Safe file URL for Django admin previews (missing uploads must not 500)."""


def safe_file_url(file_field) -> str | None:
    if not file_field:
        return None
    try:
        if not file_field.name:
            return None
        return file_field.url
    except (ValueError, OSError):
        return None
