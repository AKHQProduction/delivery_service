from typing import Any

from geopy import Location
from geopy.exc import GeocoderTimedOut
from geopy.geocoders import Nominatim

from application.common.geo import Address, GeoPayload, GeoProcessor
from infrastructure.geopy.config import GeoConfig
from infrastructure.geopy.errors import (
    AddressNotFoundByCoordinatesError,
    AddressNotFoundInCityError,
    GeolocatorBadGatewayError,
)


class PyGeoProcessor(GeoProcessor):
    def __init__(self, config: GeoConfig, geolocator: Nominatim) -> None:
        self.city = config.city
        self._geolocator = geolocator

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
            coordinates: Location | None = await self._geolocator.geocode(
                full_address,
                addressdetails=True,
                language="UA",
            )
        except GeocoderTimedOut as error:
            raise GeolocatorBadGatewayError() from error

        if coordinates is None or not self._check_address_in_city(coordinates):
            raise AddressNotFoundInCityError(address, self.city)

        return coordinates.latitude, coordinates.longitude

    async def get_location(self, coordinates: GeoPayload) -> Address:
        location: Location = await self._geolocator.reverse(
            coordinates, addressdetails=True
        )

        full_address: dict[str, Any] = location.raw.get("address", {})

        city = full_address.get("city") or full_address.get("town")
        road = full_address.get("road")
        house_number = full_address.get("house_number")

        if not all([city, road, house_number]):
            raise AddressNotFoundByCoordinatesError(coordinates)

        return Address(f"{city}, {road} {house_number}")
