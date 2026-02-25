import logging
from dataclasses import dataclass

import httpx

from backend.bootstrap.config import OSRMConfig

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class RouteGeometry:
    encoded_polyline: str
    distance_meters: int
    duration_seconds: int


class OSRMClient:
    def __init__(
        self, http_client: httpx.AsyncClient, config: OSRMConfig
    ) -> None:
        self._http = http_client
        self._base_url = config.url.rstrip("/")

    async def _request(
        self, url: str, params: dict, context: str
    ) -> dict | None:
        try:
            response = await self._http.get(url, params=params)
            response.raise_for_status()
            data = response.json()
        except httpx.HTTPStatusError as exc:
            logger.exception(
                "OSRM %s HTTP error: status=%d, url=%s",
                context,
                exc.response.status_code,
                url,
            )
            return None
        except Exception as exc:
            logger.exception(
                "OSRM %s failed [%s]", context, exc.__class__.__name__
            )
            return None

        if data.get("code") != "Ok":
            logger.error(
                "OSRM %s error: code=%s, message=%s",
                context,
                data.get("code"),
                data.get("message"),
            )
            return None
        return data

    async def get_duration_matrix(
        self, coordinates: list[tuple[float, float]]
    ) -> list[list[float]] | None:
        coords_str = ";".join(f"{lon},{lat}" for lat, lon in coordinates)
        url = f"{self._base_url}/table/v1/driving/{coords_str}"

        data = await self._request(
            url, {"annotations": "duration"}, "duration_matrix"
        )
        if data is None:
            return None

        durations = data.get("durations")
        if not durations:
            logger.error("OSRM returned Ok but durations are empty")
            return None

        sentinel = float("inf")
        return [
            [sentinel if v is None else v for v in row] for row in durations
        ]

    async def get_route_geometry(
        self, waypoints: list[tuple[float, float]]
    ) -> RouteGeometry | None:
        if len(waypoints) < 2:
            return None

        coords_str = ";".join(f"{lon},{lat}" for lat, lon in waypoints)
        url = f"{self._base_url}/route/v1/driving/{coords_str}"

        data = await self._request(
            url, {"overview": "full", "geometries": "polyline"}, "route"
        )
        if data is None:
            return None

        routes = data.get("routes")
        if not routes:
            logger.error("OSRM returned Ok but routes are empty")
            return None

        route = routes[0]
        return RouteGeometry(
            encoded_polyline=route["geometry"],
            distance_meters=int(route["distance"]),
            duration_seconds=int(route["duration"]),
        )
