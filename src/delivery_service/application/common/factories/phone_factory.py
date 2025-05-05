from delivery_service.application.ports.id_generator import IDGenerator
from delivery_service.domain.customers.customer_id import CustomerID
from delivery_service.domain.customers.phone_number import PhoneNumber


class PhoneNumberFactory:
    def __init__(self, id_generator: IDGenerator) -> None:
        self._id_generator = id_generator

    def create_phone_number(
        self, number: str, customer_id: CustomerID, *, is_primary: bool = False
    ) -> PhoneNumber:
        return PhoneNumber(
            entity_id=self._id_generator.generate_phone_number_id(),
            number=number,
            customer_id=customer_id,
            is_primary=is_primary,
        )
