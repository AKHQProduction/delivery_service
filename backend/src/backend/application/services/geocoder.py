from backend.application.dto.coordinates import CoordinatesDTO
from backend.infrastructure.nominatim import NominatimClient


class Geocoder:
    def __init__(self, nominatim_client: NominatimClient) -> None:
        self._nominatim = nominatim_client

    async def geocode(
        self, street: str, house: str, city: str
    ) -> CoordinatesDTO | None:
        return await self._nominatim.geocode(street, house, city)
