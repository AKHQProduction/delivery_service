from delivery_service.domain.addresses.address import Address
from delivery_service.domain.customers.phone_number import (
    PhoneBook,
    PhoneNumber,
)
from delivery_service.domain.shared.dto import AddressData, CoordinatesData
from delivery_service.domain.shared.entity import Entity
from delivery_service.domain.shared.shop_id import ShopID
from delivery_service.domain.shared.user_id import UserID


class Customer(Entity[UserID]):
    def __init__(
        self,
        entity_id: UserID,
        *,
        shop_id: ShopID,
        full_name: str,
        contacts: PhoneBook | None,
        delivery_addresses: list[Address],
    ) -> None:
        super().__init__(entity_id=entity_id)

        self._shop_id = shop_id
        self._full_name = full_name
        self._contacts = contacts
        self._delivery_addresses = delivery_addresses

    def edit_full_name(self, new_name: str) -> None:
        self._full_name = new_name

    def edit_primary_phone_number(self, new_phone: str) -> None:
        if self._contacts:
            self._contacts = self._contacts.change_primary_number(new_phone)
        self._contacts = PhoneBook(primary=PhoneNumber(new_phone))

    def edit_delivery_address(
        self, address_data: AddressData, coordinates_data: CoordinatesData
    ) -> None:
        pass

    @property
    def shop_reference(self) -> ShopID:
        return self._shop_id
