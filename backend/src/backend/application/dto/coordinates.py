from dataclasses import dataclass


@dataclass(frozen=True)
class CoordinatesDTO:
    latitude: float
    longitude: float
