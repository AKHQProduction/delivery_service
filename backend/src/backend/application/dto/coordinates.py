from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


class HasCoordinates(Protocol):
    latitude: float | None
    longitude: float | None


@dataclass(frozen=True)
class CoordinatesDTO:
    latitude: float
    longitude: float

    @classmethod
    def build(
        cls,
        latitude: float | None,
        longitude: float | None,
    ) -> CoordinatesDTO | None:
        if latitude is None or longitude is None:
            return None
        return cls(latitude=latitude, longitude=longitude)

    def apply_to(self, target: HasCoordinates) -> None:
        target.latitude = self.latitude
        target.longitude = self.longitude
