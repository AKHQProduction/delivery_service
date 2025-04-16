from delivery_service.domain.customers.phone_number import PhoneBook
from delivery_service.domain.shared.entity import Entity
from delivery_service.domain.shared.shop_id import ShopID
from delivery_service.domain.shared.user_id import UserID
from delivery_service.domain.shared.vo.address import DeliveryAddress


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

    @property
    def from_shop(self) -> ShopID:
        return self._shop_id
