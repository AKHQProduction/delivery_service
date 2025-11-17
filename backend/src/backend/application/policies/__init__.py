from abc import ABC, abstractmethod
from typing import Any


class Specification(ABC):
    @abstractmethod
    def is_satisfied_by(self, candidate: Any) -> bool:
        raise NotImplementedError

    def __and__(self, other: "Specification") -> "AndSpecification":
        return AndSpecification(self, other)

    def __or__(self, other: "Specification") -> "OrSpecification":
        return OrSpecification(self, other)


class AndSpecification(Specification):
    def __init__(self, *specifications: Specification) -> None:
        self._specifications = specifications

    def is_satisfied_by(self, candidate: Any) -> bool:
        return all(
            spec.is_satisfied_by(candidate) for spec in self._specifications
        )


class OrSpecification(Specification):
    def __init__(self, *specifications: Specification) -> None:
        self._specifications = specifications

    def is_satisfied_by(self, candidate: Any) -> bool:
        return any(
            spec.is_satisfied_by(candidate) for spec in self._specifications
        )
