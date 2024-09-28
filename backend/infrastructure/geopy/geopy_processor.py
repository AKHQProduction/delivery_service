from abc import ABC, abstractmethod
from typing import Any, TypeAlias

from geopy import Location
from geopy.exc import GeocoderTimedOut
from geopy.geocoders import Nominatim

from infrastructure.geopy.config import GeoConfig
from infrastructure.geopy.errors import (
    AddressNotFoundError,
    GeolocatorBadGatewayError,
)

GeoPayload: TypeAlias = tuple[float, float]
Address: TypeAlias = str


class GeoProcessor(ABC):
    @abstractmethod
    async def get_coordinates(self, address: Address) -> GeoPayload:
        raise NotImplementedError


class PyGeoProcessor(GeoProcessor):
    def __init__(self, config: GeoConfig, geolocator: Nominatim) -> None:
        self.city = config.city
        self.geolocator = geolocator

    def _check_address_in_city(self, coordinates: Location) -> bool:
        address: dict[str, Any] = coordinates.raw.get("address", {})

        location_city = address.get("city", "")
        location_town = address.get("town", "")

        house_number = address.get("house_number")

        return (
            self.city in [location_city, location_town]
            and house_number is not None
        )

    async def get_coordinates(self, address: Address) -> GeoPayload:
        full_address: str = f"{address}, {self.city}"

        try:
            coordinates: Location | None = await self.geolocator.geocode(
                full_address,
                addressdetails=True,
                language="UA",
            )
        except GeocoderTimedOut as error:
            raise GeolocatorBadGatewayError() from error

        if coordinates is None or not self._check_address_in_city(coordinates):
            raise AddressNotFoundError(address, self.city)

        return coordinates.latitude, coordinates.longitude
