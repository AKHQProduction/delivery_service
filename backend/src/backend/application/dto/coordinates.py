from dataclasses import dataclass
from typing import Protocol


class HasCoordinates(Protocol):
    latitude: float | None
    longitude: float | None


@dataclass(frozen=True)
class CoordinatesDTO:
    latitude: float
    longitude: float

    def __post_init__(self) -> None:
        object.__setattr__(self, "latitude", round(self.latitude, 4))
        object.__setattr__(self, "longitude", round(self.longitude, 4))

    @classmethod
    def build(
        cls,
        latitude: float | None,
        longitude: float | None,
    ) -> "CoordinatesDTO | None":
        if latitude is None or longitude is None:
            return None
        return cls(latitude=latitude, longitude=longitude)

    def apply_to(self, target: HasCoordinates) -> None:
        target.latitude = self.latitude
        target.longitude = self.longitude


@dataclass(frozen=True)
class AddressSuggestionDTO:
    label: str
    street: str
    house: str
    city: str
    coordinates: CoordinatesDTO | None
    district: str | None = None


@dataclass(frozen=True)
class ReverseGeocodeResult:
    display_name: str
    street: str | None
    house: str | None
    city: str | None
    district: str | None


@dataclass(frozen=True)
class EdgeInput:
    from_coords: CoordinatesDTO
    to_coords: CoordinatesDTO
