from abc import abstractmethod
from asyncio import Protocol
from typing import TypeAlias, Any

from geopy import Location
from geopy.geocoders import Nominatim

from infrastructure.geopy.config import GeoConfig
from infrastructure.geopy.errors import AddressIsNotExists

GeoPayload: TypeAlias = tuple[float, float]
Address: TypeAlias = str


class GeoProcessor(Protocol):
    @abstractmethod
    async def get_coordinates(self, address: Address) -> GeoPayload:
        raise NotImplementedError


class PyGeoProcessor(GeoProcessor):
    def __init__(
            self,
            config: GeoConfig,
            geolocator: Nominatim
    ) -> None:
        self.city = config.city
        self.geolocator = geolocator

    def _check_address_in_city(self, coordinates: Location) -> bool:
        address: dict[str, Any] = coordinates.raw.get("address", {})

        location_city = address.get("city", "")
        location_town = address.get("town", "")
        location_village = address.get("village", "")

        if self.city not in [location_city, location_town, location_village]:
            return False
        return True

    async def get_coordinates(self, address: Address) -> GeoPayload:
        full_address: str = f"{address}, {self.city}"

        coordinates: Location | None = await self.geolocator.geocode(
            full_address, addressdetails=True, language="UA"
        )

        if coordinates is None or not self._check_address_in_city(coordinates):
            raise AddressIsNotExists(address, self.city)

        return coordinates.latitude, coordinates.longitude
