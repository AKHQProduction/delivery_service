import re

from entities.common.value_objects.base import ValueObject
from entities.user.errors.user import InvalidPhoneNumberError


class PhoneNumber(ValueObject[str]):
    def _validate(self) -> None:
        pattern = r'^\+380\d{9}$'

        if not re.match(pattern, self.value):
            raise InvalidPhoneNumberError(self.value)
