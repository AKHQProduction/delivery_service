import logging
from dataclasses import dataclass

import httpx

from backend.application.dto.coordinates import CoordinatesDTO
from backend.bootstrap.config import OSRMConfig

logger = logging.getLogger(__name__)

OSRM_OK = "Ok"


@dataclass(frozen=True)
class OptimizedRoute:
    waypoint_order: list[int]


class OSRMClient:
    def __init__(
        self, http_client: httpx.AsyncClient, config: OSRMConfig
    ) -> None:
        self._http = http_client
        self._base_url = config.url.rstrip("/")
        self._enabled = config.enabled

    async def optimize_route(
        self,
        shop: CoordinatesDTO,
        waypoints: list[CoordinatesDTO],
        roundtrip: bool = True,
    ) -> OptimizedRoute | None:
        if not self._enabled:
            return None

        coords = [shop, *waypoints]
        coords_str = ";".join(f"{c.longitude},{c.latitude}" for c in coords)

        url = f"{self._base_url}/trip/v1/driving/{coords_str}"
        params = {
            "source": "first",
            "roundtrip": str(roundtrip).lower(),
        }

        logger.debug(
            "OSRM request: %d waypoints, roundtrip=%s",
            len(waypoints),
            roundtrip,
        )

        try:
            response = await self._http.get(url, params=params)
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

        if data.get("code") != OSRM_OK:
            logger.warning(
                "OSRM returned non-ok code: %s, message: %s",
                data.get("code"),
                data.get("message"),
            )
            return None

        osrm_waypoints = data.get("waypoints", [])
        order = [wp["waypoint_index"] - 1 for wp in osrm_waypoints[1:]]

        logger.debug("OSRM optimized route: %s", order)
        return OptimizedRoute(waypoint_order=order)
