import logging

import httpx

from backend.application.dto.coordinates import (
    CoordinatesDTO,
    ReverseGeocodeResult,
)
from backend.application.services.geocoder import GeocodingProvider
from backend.bootstrap.config import NominatimConfig

logger = logging.getLogger(__name__)


class NominatimClient(GeocodingProvider):
    def __init__(
        self,
        http_client: httpx.AsyncClient,
        config: NominatimConfig,
    ) -> None:
        self._http = http_client
        self._base_url = config.url.rstrip("/")

    async def geocode(
        self,
        street: str,
        house: str,
        city: str,
        *,
        require_house: bool = True,
    ) -> CoordinatesDTO | None:
        return await self._fetch(
            street, house, city, require_house=require_house
        )

    async def _fetch(
        self,
        street: str,
        house: str,
        city: str,
        *,
        require_house: bool = True,
    ) -> CoordinatesDTO | None:
        result = await self._structured_search(
            street, house, city, require_house=require_house
        )
        if result is not None:
            return result

        result = await self._freetext_search(
            street, house, city, require_house=require_house
        )
        if result is not None:
            return result

        return None

    async def _structured_search(
        self,
        street: str,
        house: str,
        city: str,
        *,
        require_house: bool = True,
    ) -> CoordinatesDTO | None:
        params = {
            "street": f"{house} {street}",
            "city": city,
            "country": "UA",
            "format": "jsonv2",
            "addressdetails": "1",
            "limit": "1",
        }
        return await self._request(
            params, house=house, require_house=require_house
        )

    async def _freetext_search(
        self,
        street: str,
        house: str,
        city: str,
        *,
        require_house: bool = True,
    ) -> CoordinatesDTO | None:
        params = {
            "q": f"{street} {house}, {city}, Україна",
            "format": "jsonv2",
            "addressdetails": "1",
            "limit": "1",
        }
        return await self._request(
            params, house=house, require_house=require_house
        )

    async def _request(
        self,
        params: dict[str, str],
        *,
        house: str = "",
        require_house: bool = True,
    ) -> CoordinatesDTO | None:
        url = f"{self._base_url}/search"

        try:
            response = await self._http.get(
                url,
                params=params,
                headers={"User-Agent": "WaterDelivery/1.0"},
            )
            response.raise_for_status()
            data = response.json()
        except httpx.HTTPStatusError as exc:
            logger.warning(
                "Nominatim HTTP error: status=%d, url=%s",
                exc.response.status_code,
                url,
            )
            return None
        except Exception as exc:
            logger.exception(
                "Nominatim request failed [%s]",
                exc.__class__.__name__,
            )
            return None

        if not data:
            return None

        first = data[0]

        address = first.get("address", {})
        if not address.get("road"):
            logger.info(
                "Nominatim result has no street: %s",
                params.get("q") or params.get("street"),
            )
            return None

        if require_house and house.strip() and not address.get("house_number"):
            logger.info(
                "Nominatim did not resolve house number: %s",
                params.get("q") or params.get("street"),
            )
            return None

        try:
            return CoordinatesDTO(
                latitude=float(first["lat"]),
                longitude=float(first["lon"]),
            )
        except (KeyError, ValueError, TypeError):
            logger.exception("Failed to parse Nominatim response: %s", first)
            return None

    async def reverse(
        self, coordinates: CoordinatesDTO
    ) -> ReverseGeocodeResult | None:
        url = f"{self._base_url}/reverse"
        params = {
            "format": "json",
            "lat": str(coordinates.latitude),
            "lon": str(coordinates.longitude),
            "addressdetails": "1",
            "accept-language": "uk",
        }

        try:
            response = await self._http.get(
                url,
                params=params,
                headers={"User-Agent": "WaterDelivery/1.0"},
            )
            response.raise_for_status()
            data = response.json()
        except httpx.HTTPStatusError as exc:
            logger.warning(
                "Nominatim reverse HTTP error: status=%d, url=%s",
                exc.response.status_code,
                url,
            )
            return None
        except Exception as exc:
            logger.exception(
                "Nominatim reverse request failed [%s]",
                exc.__class__.__name__,
            )
            return None

        try:
            address = data.get("address", {})
            return ReverseGeocodeResult(
                display_name=data["display_name"],
                street=address.get("road"),
                house=address.get("house_number"),
                city=address.get("city")
                or address.get("town")
                or address.get("village"),
                district=address.get("suburb")
                or address.get("city_district")
                or address.get("residential"),
            )
        except (KeyError, TypeError):
            logger.exception(
                "Failed to parse Nominatim reverse response: %s", data
            )
            return None
