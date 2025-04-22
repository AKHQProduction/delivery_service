from dataclasses import dataclass

from delivery_service.domain.products.product import ProductID
from delivery_service.domain.shared.new_types import FixedDecimal


@dataclass
class OrderLineData:
    product_id: ProductID
    title: str
    price_per_item: FixedDecimal
    quantity: int


@dataclass(frozen=True)
class CoordinatesData:
    latitude: float
    longitude: float


@dataclass(frozen=True)
class AddressData:
    city: str
    street: str
    house_number: str
    apartment_number: str | None
    floor: int | None
    intercom_code: str | None


@dataclass(frozen=True)
class DeliveryAddressData:
    coordinates: CoordinatesData
    address: AddressData
