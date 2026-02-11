import logging

import httpx

from backend.application.dto.coordinates import CoordinatesDTO

logger = logging.getLogger(__name__)

NOMINATIM_URL = "https://nominatim.openstreetmap.org"


class NominatimClient:
    def __init__(self, http_client: httpx.AsyncClient) -> None:
        self._http = http_client

    async def geocode(
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
        url = f"{NOMINATIM_URL}/search"

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
