from typing import cast
from uuid import UUID

from sqlalchemy import asc, delete, desc, exists, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from uuid_utils import uuid7

from backend.application.interfaces import ShopGateway
from backend.application.interfaces.gateways import Pagination, SortOrder
from backend.application.interfaces.gateways.shop_gateway import (
    CreateNewShopDTO,
    EmployeeFilters,
    EmployeeReadModel,
    ShopEmployee,
)
from backend.application.vars import ShopId, ShopRole, UserId
from backend.infrastructure.persistence.tables import (
    Role,
    Shop,
    ShopMembership,
)


class SQLAlchemyShopGateway(ShopGateway):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def relate_to_shop(self, user_id: UserId) -> bool:
        query = select(exists().where(ShopMembership.user_id == user_id))

        result = await self._session.execute(query)
        return bool(result.scalar())

    async def create_shop(self, dto: CreateNewShopDTO) -> None:
        role_query = select(Role.id).where(Role.name == ShopRole.OWNER)
        role_result = await self._session.execute(role_query)
        role_id = role_result.scalar_one()

        new_shop = Shop(
            id=dto.shop_id,
            name=dto.shop_name,
            memberships=[
                ShopMembership(
                    user_id=dto.user_id, role_id=role_id, name=dto.owner_name
                )
            ],
        )

        self._session.add(new_shop)

    async def get_shop_employee(self, user_id: UserId) -> ShopEmployee | None:
        query = (
            select(Shop.id, Role.name, ShopMembership.name)
            .join(ShopMembership, ShopMembership.shop_id == Shop.id)
            .join(Role, Role.id == ShopMembership.role_id)
            .where(ShopMembership.user_id == user_id)
        )

        result = await self._session.execute(query)
        row = result.first()

        if row:
            shop_id, role_name, full_name = row
            return ShopEmployee(
                user_id=user_id,
                shop_id=ShopId(shop_id),
                role=ShopRole(role_name),
                full_name=full_name,
            )
        return None

    async def add_employee(self, employee: ShopEmployee) -> None:
        role_query = select(Role.id).where(Role.name == employee.role)
        role_result = await self._session.execute(role_query)
        role_id = role_result.scalar_one()

        self._session.add(
            ShopMembership(
                name=employee.full_name,
                user_id=employee.user_id,
                shop_id=employee.shop_id,
                role_id=role_id,
            )
        )

    async def update_employee(self, updated_employee: ShopEmployee) -> None:
        role_query = select(Role.id).where(Role.name == updated_employee.role)
        role_result = await self._session.execute(role_query)
        role_id = role_result.scalar_one()

        query = (
            update(ShopMembership)
            .where(ShopMembership.user_id == updated_employee.user_id)
            .values(name=updated_employee.full_name, role_id=role_id)
        )

        await self._session.execute(query)

    async def delete_employee(self, user_id: UserId) -> None:
        query = delete(ShopMembership).where(ShopMembership.user_id == user_id)
        await self._session.execute(query)

    async def read_employee(self, user_id: UserId) -> EmployeeReadModel | None:
        query = (
            select(ShopMembership.name, Role.name)
            .join(Role, Role.id == ShopMembership.role_id)
            .where(ShopMembership.user_id == user_id)
        )

        result = await self._session.execute(query)
        row = result.first()

        if row:
            full_name, role_name = row
            return EmployeeReadModel(
                user_id=user_id,
                full_name=cast("str", full_name),
                role=ShopRole(cast("str", role_name)),
            )
        return None

    async def read_all_employees(
        self, filters: EmployeeFilters, pagination: Pagination
    ) -> list[EmployeeReadModel]:
        query = select(
            ShopMembership.user_id, ShopMembership.name, Role.name
        ).join(Role, Role.id == ShopMembership.role_id)

        if filters.shop_id:
            query = query.where(ShopMembership.shop_id == filters.shop_id)
        if filters.name:
            query = query.where(ShopMembership.name.ilike(f"%{filters.name}%"))

        if pagination.order == SortOrder.ASC:
            query = query.order_by(
                asc(ShopMembership.name), asc(ShopMembership.user_id)
            )
        else:
            query = query.order_by(
                desc(ShopMembership.name), asc(ShopMembership.user_id)
            )

        query = query.offset(pagination.offset).limit(pagination.limit)

        result = await self._session.execute(query)
        rows = result.all()

        return [
            EmployeeReadModel(
                user_id=UserId(cast("UUID", row[0])),
                full_name=cast("str", row[1]),
                role=ShopRole(cast("str", row[2])),
            )
            for row in rows
        ]

    def next_id(self) -> ShopId:
        return ShopId(UUID(str(uuid7())))

    async def get_shop_name(self, shop_id: ShopId) -> str | None:
        query = select(Shop.name).where(Shop.id == shop_id)
        result = await self._session.execute(query)
        return result.scalar_one_or_none()
