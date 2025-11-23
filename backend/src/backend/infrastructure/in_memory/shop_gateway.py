import uuid
from typing import Any

from backend.application.interfaces import ShopGateway
from backend.application.interfaces.gateways import Pagination, SortOrder
from backend.application.interfaces.gateways.shop_gateway import (
    CreateNewShopDTO,
    EmployeeFilters,
    EmployeeReadModel,
    ShopEmployee,
)
from backend.application.vars import ShopId, ShopRole, UserId


class InMemoryShopGateway(ShopGateway):
    def __init__(
        self,
        linked_users: set[UserId] | None = None,
        shop_id: ShopId | None = None,
    ) -> None:
        self.linked_users = set(linked_users or [])
        self.shops: dict[ShopId, Any] = {}
        self.shop_id = shop_id
        self.employees: dict[UserId, ShopEmployee] = {}
        self.employee_updated = False

    async def relate_to_shop(self, user_id: UserId) -> bool:
        return user_id in self.linked_users

    async def create_shop(self, dto: CreateNewShopDTO) -> None:
        self.shops[dto.shop_id] = {"name": dto.shop_name}
        self.linked_users.add(dto.user_id)
        self.employees[dto.user_id] = ShopEmployee(
            user_id=dto.user_id,
            shop_id=dto.shop_id,
            full_name=dto.owner_name,
            role=ShopRole.OWNER,
        )

    async def get_shop_employee(self, user_id: UserId) -> ShopEmployee | None:
        return self.employees.get(user_id)

    async def add_employee(self, employee: ShopEmployee) -> None:
        self.employees[employee.user_id] = employee

    async def update_employee(self, updated_employee: ShopEmployee) -> None:
        self.employee_updated = True

    async def delete_employee(self, user_id: UserId) -> None:
        if user_id in self.employees:
            del self.employees[user_id]
        if user_id in self.linked_users:
            self.linked_users.remove(user_id)

    async def read_employee(self, user_id: UserId) -> EmployeeReadModel | None:
        employee = self.employees.get(user_id)
        if employee:
            return EmployeeReadModel(
                user_id=employee.user_id,
                full_name=employee.full_name,
                role=employee.role,
            )
        return None

    async def read_all_employees(
        self, filters: EmployeeFilters, pagination: Pagination
    ) -> list[EmployeeReadModel]:
        employees = list(self.employees.values())

        # Apply filters
        if filters.shop_id:
            employees = [e for e in employees if e.shop_id == filters.shop_id]
        if filters.name:
            employees = [
                e
                for e in employees
                if filters.name.lower() in e.full_name.lower()
            ]

        # Sort
        employees = sorted(
            employees,
            key=lambda e: e.full_name,
            reverse=(pagination.order == SortOrder.DESC),
        )

        # Pagination
        start = pagination.offset
        end = start + pagination.limit
        employees = employees[start:end]

        return [
            EmployeeReadModel(
                user_id=e.user_id,
                full_name=e.full_name,
                role=e.role,
            )
            for e in employees
        ]

    def next_id(self) -> ShopId:
        return self.shop_id or ShopId(uuid.uuid4())
