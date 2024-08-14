import logging
from abc import abstractmethod
from asyncio import Protocol
from typing import TypeAlias, Any

from geopy import Location
from geopy.exc import GeocoderTimedOut
from geopy.geocoders import Nominatim

from infrastructure.geopy.config import GeoConfig
from infrastructure.geopy.errors import AddressIsNotExists, \
    GeolocatorBadGateway

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

        house_number = address.get("house_number", None)

        if self.city in [
            location_city,
            location_town
        ] and house_number is not None:
            return True
        return False

    async def get_coordinates(
            self,
            address: Address,
            tries: int = 0
    ) -> GeoPayload:
        full_address: str = f"{address}, {self.city}"

        try:
            coordinates: Location | None = await self.geolocator.geocode(
                full_address, addressdetails=True, language="UA"
            )
        except GeocoderTimedOut:
            logging.warning(f"The {tries} mistake in work geocoder")

            if tries <= 3:
                tries += 1
                return await self.get_coordinates(address, tries)
            else:
                raise GeolocatorBadGateway()

        if coordinates is None or not self._check_address_in_city(coordinates):
            raise AddressIsNotExists(address, self.city)

        return coordinates.latitude, coordinates.longitude
