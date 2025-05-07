import re

from delivery_service.domain.customers.customer_id import CustomerID
from delivery_service.domain.customers.phone_number_id import PhoneNumberID
from delivery_service.domain.shared.entity import Entity
from delivery_service.domain.shared.errors import ValidationError
from delivery_service.domain.shared.shop_id import ShopID

PHONE_NUMBER_PATTERN = re.compile(r"^\+380\d{9}$")


class PhoneNumber(Entity[PhoneNumberID]):
    def __init__(
        self,
        entity_id: PhoneNumberID,
        *,
        customer_id: CustomerID,
        shop_id: ShopID,
        number: str,
        is_primary: bool = False,
    ) -> None:
        super().__init__(entity_id=entity_id)

        self._customer_id = customer_id
        self._shop_id = shop_id

        self._number = number
        self._is_primary = is_primary

    def __post_init__(self) -> None:
        if not PHONE_NUMBER_PATTERN.match(self._number):
            raise ValidationError()

    def toggle_status(self) -> None:
        self._is_primary = not self.is_primary

    @property
    def customer_reference(self) -> CustomerID:
        return self._customer_id

    @property
    def phone_number(self) -> str:
        return self._number

    @property
    def is_primary(self) -> bool:
        return self._is_primary
