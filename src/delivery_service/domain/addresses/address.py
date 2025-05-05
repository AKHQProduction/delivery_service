from delivery_service.domain.addresses.address_id import AddressID
from delivery_service.domain.customers.customer_id import CustomerID
from delivery_service.domain.shared.entity import Entity
from delivery_service.domain.shared.shop_id import ShopID
from delivery_service.domain.shared.vo.address import Coordinates


class Address(Entity[AddressID]):
    def __init__(
        self,
        entity_id: AddressID,
        *,
        customer_id: CustomerID,
        shop_id: ShopID,
        city: str,
        street: str,
        house_number: str,
        apartment_number: str | None,
        floor: int | None,
        intercom_code: str | None,
        coordinates: Coordinates,
    ) -> None:
        super().__init__(entity_id=entity_id)

        self._customer_id = customer_id
        self._shop_id = shop_id

        self._city = city
        self._street = street
        self._house_number = house_number
        self._apartment_number = apartment_number
        self._floor = floor
        self._intercom_code = intercom_code
        self._coordinates = coordinates

    @property
    def address_coordinates(self) -> Coordinates:
        return self._coordinates

    def update_address_data(
        self,
        city: str,
        street: str,
        house_number: str,
        apartment_number: str | None,
        floor: int | None,
        intercom_code: str | None,
        coordinates: Coordinates,
    ) -> None:
        self._city = city
        self._street = street
        self._house_number = house_number
        self._apartment_number = apartment_number
        self._floor = floor
        self._intercom_code = intercom_code
        self._coordinates = coordinates
