from abc import ABC, abstractmethod
from typing import TypeAlias

GeoPayload: TypeAlias = tuple[float, float]
Address: TypeAlias = str


class GeoProcessor(ABC):
    @abstractmethod
    async def get_coordinates(self, address: Address) -> GeoPayload:
        raise NotImplementedError

    @abstractmethod
    async def get_location_with_coordinates(
        self, coordinates: GeoPayload
    ) -> Address:
        raise NotImplementedError

    @abstractmethod
    async def get_location_with_row(self, row: str) -> Address:
        raise NotImplementedError
