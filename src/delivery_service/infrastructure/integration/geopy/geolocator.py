from geopy import Location, Nominatim

from delivery_service.application.ports.location_finder import (
    LocationData,
    LocationFinder,
)
from delivery_service.infrastructure.integration.geopy.errors import (
    LocationNotFoundError,
)


class Geolocator(LocationFinder):
    def __init__(self, geolocator: Nominatim) -> None:
        self._geolocator = geolocator

    async def find_location(self, address: str) -> LocationData:
        location: Location | None = await self._geolocator.geocode(
            address,
            addressdetails=True,
            namedetails=True,
            language="uk",  # type: ignore[reportArgumentType]
        )

        if location:
            full_address = location.raw.get("address", {})

            city = (
                full_address.get("city")
                or full_address.get("town")
                or full_address.get("village")
            )
            street = full_address.get("road")
            house_number = full_address.get("house_number")

            if not all([city, street, house_number]):
                raise LocationNotFoundError()
            return LocationData(
                latitude=location.latitude,
                longitude=location.longitude,
                city=city,
                street=street,
                house_number=house_number,
            )
        raise LocationNotFoundError()
