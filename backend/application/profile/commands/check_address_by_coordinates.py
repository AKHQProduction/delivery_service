from dataclasses import dataclass

from application.common.geo import GeoProcessor


@dataclass(frozen=True)
class CheckAddressByCoordinatesInputData:
    coordinates: tuple[float, float]


@dataclass(frozen=True)
class CheckAddressByCoordinatesOutputData:
    address: str


@dataclass
class CheckAddressByCoordinates:
    geo: GeoProcessor

    async def __call__(
        self, data: CheckAddressByCoordinatesInputData
    ) -> CheckAddressByCoordinatesOutputData:
        address = await self.geo.get_location_with_coordinates(
            data.coordinates
        )

        return CheckAddressByCoordinatesOutputData(address=address)
