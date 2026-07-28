from datetime import date
from typing import Annotated

from pydantic import StringConstraints

PHONE_NUMBER_PATTERN = r"^\d{10}$"
PhoneNumberStr = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=10,
        max_length=10,
        pattern=PHONE_NUMBER_PATTERN,
    ),
]


def validate_dob_before_today(value: date | None) -> date | None:
    if value is not None and value >= date.today():
        raise ValueError("Date of birth must be before today.")
    return value
