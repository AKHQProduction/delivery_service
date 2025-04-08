from abc import abstractmethod
from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class LocationCoordinates:
    latitude: float
    longitude: float


class LocationFinder(Protocol):
    @abstractmethod
    async def find_location(self, address: str) -> LocationCoordinates:
        raise NotImplementedError
