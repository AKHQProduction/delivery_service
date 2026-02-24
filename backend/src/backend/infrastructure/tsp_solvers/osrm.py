import logging

import httpx

from backend.bootstrap.config import OSRMConfig

logger = logging.getLogger(__name__)


class OSRMClient:
    def __init__(
        self, http_client: httpx.AsyncClient, config: OSRMConfig
    ) -> None:
        self._http = http_client
        self._base_url = config.url.rstrip("/")

    async def get_duration_matrix(
        self, coordinates: list[tuple[float, float]]
    ) -> list[list[float]] | None:
        coords_str = ";".join(f"{lon},{lat}" for lat, lon in coordinates)
        url = f"{self._base_url}/table/v1/driving/{coords_str}"

        try:
            response = await self._http.get(
                url, params={"annotations": "duration"}
            )
            response.raise_for_status()
            data = response.json()
        except httpx.HTTPStatusError as exc:
            logger.exception(
                "OSRM HTTP error: status=%d, url=%s",
                exc.response.status_code,
                url,
            )
            return None
        except Exception as exc:
            logger.exception(
                "OSRM request failed [%s]",
                exc.__class__.__name__,
            )
            return None

        if data.get("code") != "Ok":
            logger.error(
                "OSRM error: code=%s, message=%s",
                data.get("code"),
                data.get("message"),
            )
            return None

        durations = data.get("durations")
        if not durations:
            logger.error("OSRM returned Ok but durations are empty")
            return None

        sentinel = float("inf")
        return [
            [sentinel if v is None else v for v in row] for row in durations
        ]
