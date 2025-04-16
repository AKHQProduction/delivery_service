from abc import abstractmethod
from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class LocationData:
    latitude: float
    longitude: float
    city: str
    street: str
    house_number: str


class LocationFinder(Protocol):
    @abstractmethod
    async def find_location(self, address: str) -> LocationData:
        raise NotImplementedError
