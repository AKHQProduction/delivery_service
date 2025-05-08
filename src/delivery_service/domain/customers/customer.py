from delivery_service.domain.addresses.address import Address
from delivery_service.domain.addresses.address_id import AddressID
from delivery_service.domain.customers.customer_id import CustomerID
from delivery_service.domain.customers.phone_number import (
    PhoneNumber,
)
from delivery_service.domain.customers.phone_number_id import PhoneNumberID
from delivery_service.domain.shared.dto import AddressData, CoordinatesData
from delivery_service.domain.shared.entity import Entity
from delivery_service.domain.shared.shop_id import ShopID
from delivery_service.domain.shared.user_id import UserID
from delivery_service.domain.shared.vo.address import Coordinates


class Customer(Entity[CustomerID]):
    def __init__(
        self,
        entity_id: CustomerID,
        *,
        shop_id: ShopID,
        name: str,
        contacts: list[PhoneNumber],
        delivery_addresses: list[Address],
        user_id: UserID | None = None,
    ) -> None:
        super().__init__(entity_id=entity_id)

        self._shop_id = shop_id
        self._user_id = user_id
        self._name = name
        self._contacts = contacts
        self._delivery_addresses = delivery_addresses

    def edit_name(self, new_name: str) -> None:
        self._name = new_name

    def add_address(self, address: Address) -> None:
        self._delivery_addresses.append(address)

    def delete_address(self, address_id: AddressID) -> None:
        for address in self._delivery_addresses:
            if address.entity_id == address_id:
                self._delivery_addresses.remove(address)

    def edit_primary_phone_number(self, new_phone: PhoneNumberID) -> None:
        if self._contacts:
            old_primary_number = self._get_primary_phone_number()
            old_primary_number.toggle_status()

            for number in self._contacts:
                if number.entity_id == new_phone:
                    number.toggle_status()
        raise ValueError()

    def edit_delivery_address(
        self, address_data: AddressData, coordinates_data: CoordinatesData
    ) -> None:
        self._delivery_addresses[0].update_address_data(
            city=address_data.city,
            street=address_data.street,
            house_number=address_data.house_number,
            apartment_number=address_data.apartment_number,
            floor=address_data.floor,
            intercom_code=address_data.intercom_code,
            coordinates=Coordinates(
                latitude=coordinates_data.latitude,
                longitude=coordinates_data.longitude,
            ),
        )

    def _get_primary_phone_number(self) -> PhoneNumber:
        for number in self._contacts:
            if number.is_primary:
                return number
        raise ValueError()

    @property
    def shop_reference(self) -> ShopID:
        return self._shop_id
