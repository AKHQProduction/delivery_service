from typing import Any

from application.common.specification import Specification


class HasLessLength(Specification):
    def __init__(self, length: int):
        self.length = length

    def is_satisfied_by(self, candidate: Any) -> bool:
        return len(candidate) < self.length


class HasGreateLength(Specification):
    def __init__(self, length: int):
        self.length = length

    def is_satisfied_by(self, candidate: Any) -> bool:
        return len(candidate) > self.length
