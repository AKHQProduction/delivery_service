from typing import AsyncGenerator

from geopy import Nominatim
from geopy.adapters import AioHTTPAdapter


async def get_geolocator() -> AsyncGenerator[Nominatim, None]:
    async with Nominatim(
        user_agent="My GeoPy agent",
        adapter_factory=AioHTTPAdapter,
        timeout=10,  # type: ignore[reportArgumentType]
    ) as geolocator:
        yield geolocator
