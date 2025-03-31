from typing import Any

from geopy import Location
from geopy.exc import GeocoderTimedOut
from geopy.geocoders import Nominatim

from application.common.geo import Address, GeoPayload, GeoProcessor
from infrastructure.geopy.config import GeoConfig
from infrastructure.geopy.errors import (
    GeolocatorBadGatewayError,
    InvalidAddressInputError,
)


class PyGeoProcessor(GeoProcessor):
    def __init__(self, config: GeoConfig, geolocator: Nominatim) -> None:
        self._geolocator = geolocator

    async def get_coordinates(self, address: Address) -> GeoPayload:
        try:
            coordinates: Location | None = await self._geolocator.geocode(
                address,
                addressdetails=True,
                language="UA",
            )
        except GeocoderTimedOut as error:
            raise GeolocatorBadGatewayError() from error

        return GeoPayload(coordinates.latitude, coordinates.longitude)

    async def get_location_with_coordinates(
        self, coordinates: GeoPayload
    ) -> Address:
        location: Location | None = await self._geolocator.reverse(
            coordinates, addressdetails=True
        )

        if not location:
            InvalidAddressInputError()

        return self._check_location(location)

    async def get_location_with_row(self, row: str) -> Address:
        location: Location | None = await self._geolocator.geocode(
            row, addressdetails=True, namedetails=True
        )

        if not location:
            InvalidAddressInputError()

        return self._check_location(location)

    def _check_location(self, location: Location) -> Address:
        full_address: dict[str, Any] = location.raw.get("address", {})

        city = full_address.get("city") or full_address.get("town")
        road = full_address.get("road")
        house_number = full_address.get("house_number")

        if not all([city, road, house_number]):
            raise InvalidAddressInputError()

        return Address(f"{city}, {road} {house_number}")
