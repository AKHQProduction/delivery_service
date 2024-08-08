import re

from backend.domain.common.value_objects.base import ValueObject
from backend.domain.errors.user import InvalidPhoneNumber


class PhoneNumber(ValueObject[str]):
    value: str

    def _validate(self) -> None:
        pattern = r'^\+380\d{9}$'

        if not re.match(pattern, self.value):
            raise InvalidPhoneNumber(self.value)
