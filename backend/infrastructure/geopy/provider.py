import logging
from typing import AsyncGenerator

from geopy import Nominatim
from geopy.adapters import AioHTTPAdapter

from infrastructure.geopy.config import GeoConfig


async def get_geolocator(config: GeoConfig) -> AsyncGenerator[Nominatim, None]:
    async with Nominatim(
            user_agent=config.user_agent,
            adapter_factory=AioHTTPAdapter,
            timeout=10
    ) as geolocator:
        logging.info("Geolocator was created.")

        yield geolocator

        logging.info("Geolocator was stop.")
