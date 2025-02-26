from dataclasses import dataclass

from geopy import Location, Nominatim

from delivery_service.core.shared.location import Location as LocationVO


@dataclass
class Coordinates:
    latitude: float
    longitude: float


class Geolocator:
    def __init__(self, geolocator: Nominatim) -> None:
        self._geolocator = geolocator

    async def get_location_data(self, address: str) -> LocationVO:
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

            # raise BL error
            if not all([city, street, house_number]):
                raise ValueError()
            return LocationVO(
                city=city,
                street=street,
                house_number=house_number,
                latitude=location.latitude,
                longitude=location.longitude,
            )
        # raise BL error
        raise ValueError()
