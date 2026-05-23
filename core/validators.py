import re

from core.exceptions import ServiceException

BD_MOBILE_REGEX = re.compile(r"^\+8801[0-9]{9}$")


def validate_bd_mobile(value: str) -> str:
    if not BD_MOBILE_REGEX.match(value):
        raise ServiceException(code="INVALID_MOBILE", message="Invalid mobile format")
    return value
