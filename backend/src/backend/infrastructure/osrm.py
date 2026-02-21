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

    async def optimize_route(
        self,
        shop: CoordinatesDTO,
        waypoints: list[CoordinatesDTO],
        roundtrip: bool = True,
    ) -> OptimizedRoute | None:
        coords = [shop, *waypoints]
        coords_str = ";".join(f"{c.longitude},{c.latitude}" for c in coords)

        url = f"{self._base_url}/trip/v1/driving/{coords_str}"
        params: dict[str, str] = {
            "source": "first",
            "roundtrip": str(roundtrip).lower(),
        }
        if not roundtrip:
            params["destination"] = "last"

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
        order = sorted(
            range(len(osrm_waypoints) - 1),
            key=lambda i: osrm_waypoints[i + 1]["waypoint_index"],
        )

        logger.debug("OSRM optimized route: %s", order)
        return OptimizedRoute(waypoint_order=order)

    async def get_durations_from_shop(
        self,
        shop: CoordinatesDTO,
        waypoints: list[CoordinatesDTO],
    ) -> list[float] | None:
        coords = [shop, *waypoints]
        coords_str = ";".join(f"{c.longitude},{c.latitude}" for c in coords)

        url = f"{self._base_url}/table/v1/driving/{coords_str}"
        params = {"sources": "0", "annotations": "duration"}

        try:
            response = await self._http.get(url, params=params)
            response.raise_for_status()
            data = response.json()
        except httpx.HTTPStatusError as exc:
            logger.error(
                "OSRM Table HTTP error: status=%d, url=%s",
                exc.response.status_code,
                url,
            )
            return None
        except Exception as exc:
            logger.error(
                "OSRM Table request failed [%s]",
                exc.__class__.__name__,
            )
            return None

        if data.get("code") != OSRM_OK:
            logger.error(
                "OSRM Table returned non-ok code: %s, message: %s",
                data.get("code"),
                data.get("message"),
            )
            return None

        durations_row = data.get("durations", [[]])[0]
        return durations_row[1:]
