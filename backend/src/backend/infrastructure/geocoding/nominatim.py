import logging

import httpx

from backend.application.dto.coordinates import (
    AddressSuggestionDTO,
    CoordinatesDTO,
    ReverseGeocodeResult,
)
from backend.application.services.geocoder import GeocodingProvider
from backend.bootstrap.config import NominatimConfig

logger = logging.getLogger(__name__)
SUGGEST_RAW_LIMIT = 10


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

    async def suggest(
        self,
        query: str,
        city: str,
        *,
        limit: int = 5,
    ) -> list[AddressSuggestionDTO]:
        if limit <= 0:
            return []

        url = f"{self._base_url}/search"
        params = {
            "q": f"{query}, {city}, Україна",
            "format": "jsonv2",
            "addressdetails": "1",
            "limit": str(max(limit, SUGGEST_RAW_LIMIT)),
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
                "Nominatim suggest HTTP error: status=%d, url=%s",
                exc.response.status_code,
                url,
            )
            return []
        except Exception as exc:
            logger.exception(
                "Nominatim suggest request failed [%s]",
                exc.__class__.__name__,
            )
            return []

        if not isinstance(data, list):
            return []

        suggestions: list[AddressSuggestionDTO] = []
        for item in data:
            if not isinstance(item, dict):
                continue
            suggestion = self._normalize_suggestion(item)
            if suggestion is not None:
                suggestions.append(suggestion)

        if not suggestions:
            return []

        suggestions.sort(key=lambda item: not item.house)
        return suggestions[:limit]

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

    @staticmethod
    def _normalize_text(value: object | None) -> str:
        if not isinstance(value, str):
            return ""
        text = value.strip()
        if not text or text.lower() == "none":
            return ""
        return text

    @classmethod
    def _build_suggestion_label(
        cls,
        *,
        street: str,
        house: str,
        district: str,
        city: str,
    ) -> str:
        street_line = ", ".join(part for part in [street, house] if part)
        return ", ".join(
            part for part in [street_line, district, city] if part
        )

    def _normalize_suggestion(
        self,
        item: dict[str, object],
    ) -> AddressSuggestionDTO | None:
        try:
            address = item.get("address", {})
            if not isinstance(address, dict):
                return None

            street = self._normalize_text(address.get("road"))
            if not street:
                return None

            city = (
                self._normalize_text(address.get("city"))
                or self._normalize_text(address.get("town"))
                or self._normalize_text(address.get("village"))
            )
            if not city:
                return None

            district = (
                self._normalize_text(address.get("quarter"))
                or self._normalize_text(address.get("suburb"))
                or self._normalize_text(address.get("city_district"))
                or self._normalize_text(address.get("residential"))
            )

            lat = item.get("lat")
            lon = item.get("lon")
            if not isinstance(lat, (str, int, float)) or not isinstance(
                lon, (str, int, float)
            ):
                return None

            coordinates = CoordinatesDTO(
                latitude=float(lat),
                longitude=float(lon),
            )

            house = self._normalize_text(address.get("house_number"))
            label = self._build_suggestion_label(
                street=street,
                house=house,
                district=district,
                city=city,
            )

            return AddressSuggestionDTO(
                label=label,
                street=street,
                house=house,
                city=city,
                coordinates=coordinates,
                district=district or None,
            )
        except (KeyError, TypeError, ValueError):
            logger.exception(
                "Failed to parse Nominatim suggest response: %s", item
            )
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
                district=address.get("quarter")
                or address.get("suburb")
                or address.get("city_district")
                or address.get("residential"),
            )
        except (KeyError, TypeError):
            logger.exception(
                "Failed to parse Nominatim reverse response: %s", data
            )
            return None
