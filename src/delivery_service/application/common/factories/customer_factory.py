from delivery_service.application.ports.id_generator import IDGenerator
from delivery_service.domain.customers.customer import Customer
from delivery_service.domain.customers.phone_number import (
    PhoneBook,
    PhoneNumber,
)
from delivery_service.domain.shared.shop_id import ShopID


class CustomerFactory:
    def __init__(self, id_generator: IDGenerator) -> None:
        self._id_generator = id_generator

    def create_customer(
        self, shop_id: ShopID, full_name: str, phone_number: str
    ) -> Customer:
        return Customer(
            entity_id=self._id_generator.generate_user_id(),
            shop_id=shop_id,
            full_name=full_name,
            contacts=PhoneBook(primary=PhoneNumber(phone_number)),
            delivery_address=None,
        )
