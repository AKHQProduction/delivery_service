from domain.common.value_objects.base import ValueObject


class UserId(ValueObject[int]):
    value: int
