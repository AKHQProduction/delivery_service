from delivery_service.domain.customers.phone_number import (
    PhoneBook,
    PhoneNumber,
)
from delivery_service.domain.shared.entity import Entity
from delivery_service.domain.shared.shop_id import ShopID
from delivery_service.domain.shared.user_id import UserID
from delivery_service.domain.shared.vo.address import (
    Address,
    AddressData,
    Coordinates,
    CoordinatesData,
    DeliveryAddress,
)


class Customer(Entity[UserID]):
    def __init__(
        self,
        entity_id: UserID,
        *,
        shop_id: ShopID,
        full_name: str,
        contacts: PhoneBook | None,
        delivery_address: DeliveryAddress | None,
    ) -> None:
        super().__init__(entity_id=entity_id)

        self._shop_id = shop_id
        self._full_name = full_name
        self._contacts = contacts
        self._delivery_address = delivery_address

    def edit_full_name(self, new_name: str) -> None:
        self._full_name = new_name

    def edit_primary_phone_number(self, new_phone: str) -> None:
        if self._contacts:
            self._contacts = self._contacts.change_primary_number(new_phone)
        self._contacts = PhoneBook(primary=PhoneNumber(new_phone))

    def edit_delivery_address(
        self, address_data: AddressData, coordinates_data: CoordinatesData
    ) -> None:
        if self._delivery_address:
            self._delivery_address = (
                self._delivery_address.edit_delivery_address(
                    address_data, coordinates_data
                )
            )
        self._delivery_address = DeliveryAddress(
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

    @property
    def from_shop(self) -> ShopID:
        return self._shop_id
