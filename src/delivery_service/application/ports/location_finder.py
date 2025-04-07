from abc import abstractmethod
from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class LocationData:
    city: str
    street: str
    house_number: str
    latitude: float
    longitude: float


class LocationFinder(Protocol):
    @abstractmethod
    async def find_location(self, address: str) -> LocationData:
        raise NotImplementedError
