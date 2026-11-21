import re

PHONE_REGEX = r"^\+?[0-9]{10,15}$"
PINCODE_REGEX = r"^[1-9][0-9]{5}$"


def validate_phone(phone: str) -> bool:
    return bool(re.match(PHONE_REGEX, phone))


def validate_pincode(pincode: str) -> bool:
    return bool(re.match(PINCODE_REGEX, pincode))
