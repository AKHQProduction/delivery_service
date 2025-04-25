from dataclasses import dataclass

from delivery_service.domain.shared.dto import AddressData, CoordinatesData


@dataclass(slots=True, frozen=True, eq=True, unsafe_hash=True)
class Coordinates:
    latitude: float
    longitude: float

    @property
    def coordinates(self) -> tuple[float, float]:
        return self.latitude, self.longitude


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
