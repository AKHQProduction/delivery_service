from dataclasses import dataclass

from application.common.geo import GeoProcessor


@dataclass(frozen=True)
class CheckAddressByRowInputData:
    row_address: str


@dataclass(frozen=True)
class CheckAddressByRowOutputData:
    address: str


@dataclass
class CheckAddressByRow:
    geo: GeoProcessor

    async def __call__(
        self, data: CheckAddressByRowInputData
    ) -> CheckAddressByRowOutputData:
        address = await self.geo.get_location_with_row(data.row_address)

        return CheckAddressByRowOutputData(address=address)
