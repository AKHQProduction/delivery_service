from __future__ import annotations

from dataclasses import dataclass


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
