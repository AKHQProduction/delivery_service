from dataclasses import dataclass


@dataclass(slots=True, frozen=True, eq=True, unsafe_hash=True)
class Coordinates:
    latitude: float
    longitude: float

    @property
    def coordinates(self) -> tuple[float, float]:
        return self.latitude, self.longitude


@dataclass(slots=True, frozen=True, eq=True, unsafe_hash=True)
class Location:
    city: str
    street: str
    house_number: str

    @property
    def full_address(self) -> str:
        return f"{self.city}, {self.street} {self.house_number}"
