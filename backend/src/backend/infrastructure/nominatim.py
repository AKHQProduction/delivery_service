import logging

import httpx

from backend.application.dto.coordinates import CoordinatesDTO
from backend.bootstrap.config import NominatimConfig
from backend.infrastructure.persistence.gateways.geocode_cache import (
    RedisGeocodeCache,
)

logger = logging.getLogger(__name__)


class NominatimClient:
    def __init__(
        self,
        http_client: httpx.AsyncClient,
        config: NominatimConfig,
        cache: RedisGeocodeCache,
    ) -> None:
        self._http = http_client
        self._base_url = config.url.rstrip("/")
        self._cache = cache

    async def geocode(
        self, street: str, house: str, city: str
    ) -> CoordinatesDTO | None:
        cached = await self._cache.get(city, street, house)
        if cached is not None:
            return cached

        result = await self._fetch(street, house, city)
        if result is not None:
            await self._cache.set(city, street, house, result)

        return result

    async def _fetch(
        self, street: str, house: str, city: str
    ) -> CoordinatesDTO | None:
        logger.debug(
            "Geocoding address: street=%s, house=%s, city=%s",
            street,
            house,
            city,
        )

        result = await self._structured_search(street, house, city)
        if result is not None:
            logger.info(
                "Geocoded via structured search: %s %s, %s -> (%s, %s)",
                street,
                house,
                city,
                result.latitude,
                result.longitude,
            )
            return result

        logger.debug(
            "Structured search empty, trying freetext: %s %s, %s",
            street,
            house,
            city,
        )

        result = await self._freetext_search(street, house, city)
        if result is not None:
            logger.info(
                "Geocoded via freetext search: %s %s, %s -> (%s, %s)",
                street,
                house,
                city,
                result.latitude,
                result.longitude,
            )
            return result

        logger.warning(
            "Geocoding failed: no results for %s %s, %s",
            street,
            house,
            city,
        )
        return None

    async def _structured_search(
        self, street: str, house: str, city: str
    ) -> CoordinatesDTO | None:
        params = {
            "street": f"{house} {street}",
            "city": city,
            "country": "UA",
            "format": "jsonv2",
            "limit": "1",
        }
        return await self._request(params)

    async def _freetext_search(
        self, street: str, house: str, city: str
    ) -> CoordinatesDTO | None:
        params = {
            "q": f"{street} {house}, {city}, Україна",
            "format": "jsonv2",
            "limit": "1",
        }
        return await self._request(params)

    async def _request(self, params: dict[str, str]) -> CoordinatesDTO | None:
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
            logger.exception(
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
        try:
            return CoordinatesDTO(
                latitude=float(first["lat"]),
                longitude=float(first["lon"]),
            )
        except (KeyError, ValueError, TypeError):
            logger.exception("Failed to parse Nominatim response: %s", first)
            return None

    async def reverse_raw(self, coordinates: CoordinatesDTO) -> dict | None:
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
            return response.json()
        except httpx.HTTPStatusError as exc:
            logger.exception(
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
