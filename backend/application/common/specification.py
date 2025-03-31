from abc import ABC, abstractmethod
from typing import Any


class Specification(ABC):
    @abstractmethod
    def is_satisfied_by(self, candidate: Any) -> bool:
        raise NotImplementedError

    def __and__(self, other: "Specification") -> "Specification":
        return _And(self, other)

    def __or__(self, other: "Specification") -> "Specification":
        return _Or(self, other)

    def __invert__(self) -> "Specification":
        return _Invert(self)


class _CompositeSpecification(Specification, ABC):
    pass


class _MultipleCompositeSpecification(_CompositeSpecification, ABC):
    def __init__(self, *specifications: Specification):
        self.specifications = specifications


class _And(_MultipleCompositeSpecification):
    def __and__(self, other: Specification):
        if isinstance(other, _And):
            return _And(*self.specifications, *other.specifications)
        return _And(*self.specifications, other)

    def is_satisfied_by(self, candidate: Any) -> bool:
        return all(
            specification.is_satisfied_by(candidate)
            for specification in self.specifications
        )


class _Or(_MultipleCompositeSpecification):
    def __or__(self, other: Specification):
        if isinstance(other, _Or):
            return _Or(*self.specifications, *other.specifications)
        return _Or(*self.specifications, other)

    def is_satisfied_by(self, candidate: Any) -> bool:
        return any(
            specification.is_satisfied_by(candidate)
            for specification in self.specifications
        )


class _UnaryCompositeSpecification(_CompositeSpecification, ABC):
    def __init__(self, specification: Specification):
        self.specification = specification


class _Invert(_UnaryCompositeSpecification):
    def is_satisfied_by(self, candidate: Any) -> bool:
        return not self.specification.is_satisfied_by(candidate)
