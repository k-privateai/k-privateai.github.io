"""
utils
"""

from typing import Any
from math import isnan

from phonenumbers import PhoneNumber, format_number, PhoneNumberFormat


def get_data(data: Any) -> None | Any:
    return (
        None
        if isinstance(data, float) and isnan(data)
        else (data.strip() if isinstance(data, str) else data)
    )


def get_phone_number_str(phone_number: PhoneNumber | None) -> str:
    return (
        phone_number  # type:ignore
        if phone_number is None
        else format_number(phone_number, PhoneNumberFormat.INTERNATIONAL)
    )
