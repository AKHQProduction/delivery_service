from delivery_service.domain.customers.customer import Customer
from delivery_service.domain.customers.phone_number import (
    PhoneBook,
    PhoneNumber,
)
from delivery_service.domain.shared.entity import Entity
from delivery_service.domain.shared.errors import AccessDeniedError
from delivery_service.domain.shared.shop_id import ShopID
from delivery_service.domain.shared.user_id import UserID
from delivery_service.domain.shared.vo.address import (
    Address,
    AddressData,
    Coordinates,
    CoordinatesData,
    DeliveryAddress,
    DeliveryAddressData,
)
from delivery_service.domain.staff.staff_member import StaffMember
from delivery_service.domain.staff.staff_role import Role


class CustomerRegistry(Entity[ShopID]):
    def __init__(
        self, entity_id: ShopID, *, staff_members: list[StaffMember]
    ) -> None:
        super().__init__(entity_id=entity_id)

        self._staff_members = staff_members

    def add_new_customer(
        self,
        new_customer_id: UserID,
        full_name: str,
        primary_phone_number: str,
        delivery_data: DeliveryAddressData | None,
        creator_id: UserID,
    ) -> Customer:
        self._member_with_admin_roles(candidate_id=creator_id)

        delivery_address = (
            None
            if not delivery_data
            else DeliveryAddress(
                coordinates=Coordinates(
                    latitude=delivery_data.coordinates.latitude,
                    longitude=delivery_data.coordinates.longitude,
                ),
                address=Address(
                    city=delivery_data.address.city,
                    street=delivery_data.address.street,
                    house_number=delivery_data.address.house_number,
                    apartment_number=delivery_data.address.apartment_number,
                    floor=delivery_data.address.floor,
                    intercom_code=delivery_data.address.intercom_code,
                ),
            )
        )

        return Customer(
            entity_id=new_customer_id,
            shop_id=self.entity_id,
            full_name=full_name,
            contacts=PhoneBook(primary=PhoneNumber(primary_phone_number)),
            delivery_address=delivery_address,
        )

    def can_delete_customer(
        self, customer: Customer, deleter_id: UserID
    ) -> None:
        self._is_current_shop_customer(customer.from_shop)
        self._member_with_admin_roles(deleter_id)

    def edit_customer_full_name(
        self, customer: Customer, editor_id: UserID, new_name: str
    ) -> None:
        self._is_current_shop_customer(customer.from_shop)
        self._member_with_admin_roles(editor_id)

        customer.edit_full_name(new_name)

    def edit_customer_primary_phone(
        self, customer: Customer, editor_id: UserID, new_phone: str
    ) -> None:
        self._is_current_shop_customer(customer.from_shop)
        self._member_with_admin_roles(editor_id)

        customer.edit_primary_phone_number(new_phone)

    def edit_customer_address(
        self,
        customer: Customer,
        editor_id: UserID,
        address: AddressData,
        coordinates: CoordinatesData,
    ) -> None:
        self._is_current_shop_customer(customer.from_shop)
        self._member_with_admin_roles(editor_id)

        customer.edit_delivery_address(
            address_data=address, coordinates_data=coordinates
        )

    def _check_roles(
        self, required_roles: list[Role], candidate_id: UserID
    ) -> None:
        current_staff_member = next(
            (
                member
                for member in self._staff_members
                if member.entity_id == candidate_id
            ),
            None,
        )
        if not current_staff_member:
            raise AccessDeniedError()
        if not any(
            current_staff_member.has_role(role) for role in required_roles
        ):
            raise AccessDeniedError()

    def _member_with_admin_roles(self, candidate_id: UserID) -> None:
        self._check_roles(
            required_roles=[Role.SHOP_OWNER, Role.SHOP_MANAGER],
            candidate_id=candidate_id,
        )

    def _is_current_shop_customer(self, customer_shop_id: ShopID) -> None:
        if not (customer_shop_id == self.id):
            raise AccessDeniedError()

    @property
    def id(self) -> ShopID:
        return self.entity_id
