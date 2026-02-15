from typing import cast


def mapped_cast[T](tp: type[T], value: object) -> T:
    return cast("T", value)
