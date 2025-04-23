import math
from dataclasses import dataclass
from typing import Final

from delivery_service.domain.shared.dto import AddressData, CoordinatesData

EARTH_RADIUS: Final[int] = 6371


@dataclass(slots=True, frozen=True, eq=True, unsafe_hash=True)
class Coordinates:
    latitude: float
    longitude: float

    @property
    def coordinates(self) -> tuple[float, float]:
        return self.latitude, self.longitude

    def distance_to(self, other: "Coordinates") -> float:
        """
        Calculate the distance between two points in km.
        Using the haversine formula

        :param Coordinates other: The second point

        :return: Distance between two points in kilometers
        :rtype: float
        """
        # Converting degrees to radians
        self_latitude_radians = math.radians(self.latitude)
        other_latitude_radians = math.radians(other.latitude)
        self_longitude_radians = math.radians(self.longitude)
        other_longitude_radians = math.radians(other.longitude)

        latitude_delta = other_latitude_radians - self_latitude_radians
        longitude_delta = other_longitude_radians - self_longitude_radians

        haversine_latitude = math.sin(latitude_delta / 2) ** 2
        haversine_longitude = math.sin(longitude_delta / 2) ** 2

        haversine_formula = (
            haversine_latitude
            + math.cos(self_latitude_radians)
            * math.cos(other_latitude_radians)
            * haversine_longitude
        )

        central_angle = 2 * math.atan2(
            math.sqrt(haversine_formula), math.sqrt(1 - haversine_formula)
        )

        return EARTH_RADIUS * central_angle


@dataclass(slots=True, frozen=True, eq=True, unsafe_hash=True)
class Address:
    city: str
    street: str
    house_number: str
    apartment_number: str | None
    floor: int | None
    intercom_code: str | None

    @property
    def full_address(self) -> str:
        return f"{self.city}, {self.street} {self.house_number}"


@dataclass(slots=True, frozen=True, eq=True, unsafe_hash=True)
class DeliveryAddress:
    coordinates: Coordinates
    address: Address

    def edit_delivery_address(
        self, address_data: AddressData, coordinates_data: CoordinatesData
    ) -> "DeliveryAddress":
        return DeliveryAddress(
            coordinates=Coordinates(
                latitude=coordinates_data.latitude,
                longitude=coordinates_data.longitude,
            ),
            address=Address(
                city=address_data.city,
                street=address_data.street,
                house_number=address_data.house_number,
                apartment_number=address_data.apartment_number,
                floor=address_data.floor,
                intercom_code=address_data.intercom_code,
            ),
        )
