from delivery_service.application.ports.id_generator import IDGenerator
from delivery_service.domain.addresses.address import Address
from delivery_service.domain.customers.customer_id import CustomerID
from delivery_service.domain.shared.dto import AddressData, CoordinatesData
from delivery_service.domain.shared.shop_id import ShopID
from delivery_service.domain.shared.vo.address import Coordinates


class AddressFactory:
    def __init__(self, id_generator: IDGenerator) -> None:
        self._id_generator = id_generator

    def create_address(
        self,
        address_data: AddressData,
        coordinates_data: CoordinatesData,
        customer_id: CustomerID,
        shop_id: ShopID,
    ) -> Address:
        return Address(
            entity_id=self._id_generator.generate_address_id(),
            customer_id=customer_id,
            shop_id=shop_id,
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
