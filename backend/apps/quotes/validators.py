import re

from django.core.exceptions import ValidationError


def validate_ru_phone(value: str) -> str:
    digits = re.sub(r"\D", "", value)
    if digits.startswith("8") and len(digits) == 11:
        digits = "7" + digits[1:]
    if not digits.startswith("7") or len(digits) != 11:
        raise ValidationError("Телефон должен быть в формате +7 (XXX) XXX-XX-XX")
    return f"+{digits}"


def validate_inn(value: str) -> str:
    if not value:
        return ""
    digits = re.sub(r"\D", "", value)
    if len(digits) not in (10, 12):
        raise ValidationError("ИНН должен содержать 10 или 12 цифр")
    return digits


def validate_kpp(value: str) -> str:
    if not value:
        return ""
    digits = re.sub(r"\D", "", value)
    if len(digits) != 9:
        raise ValidationError("КПП должен содержать 9 цифр")
    return digits
