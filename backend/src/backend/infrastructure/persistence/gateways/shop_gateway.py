from uuid import UUID

from sqlalchemy import exists, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from uuid_utils.compat import uuid7

from backend.application.dto.gateways import Pagination
from backend.application.dto.gateways.shop_gateway import (
    EmployeeFilters,
    EmployeeReadModel,
)
from backend.application.vars import ShopId, ShopRole, UserId
from backend.infrastructure.persistence.tables import (
    Role,
    Shop,
    ShopMembership,
)
from backend.infrastructure.persistence.utils.cast import mapped_cast
from backend.infrastructure.persistence.utils.escape import escape_like
from backend.infrastructure.persistence.utils.sorting import apply_sorting


class SQLAlchemyShopGateway:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def save(self, entity: Shop | ShopMembership) -> None:
        self._session.add(entity)

    async def load_membership(self, user_id: UserId) -> ShopMembership | None:
        query = (
            select(ShopMembership)
            .options(joinedload(ShopMembership.role))
            .where(ShopMembership.user_id == user_id)
        )
        result = await self._session.execute(query)
        return result.scalar_one_or_none()

    async def delete_membership(self, membership: ShopMembership) -> None:
        await self._session.delete(membership)

    async def get_role_id(self, role: ShopRole) -> int:
        query = select(Role.id).where(Role.name == role)
        result = await self._session.execute(query)
        return result.scalar_one()

    async def relate_to_shop(self, user_id: UserId) -> bool:
        query = select(exists().where(ShopMembership.user_id == user_id))
        result = await self._session.execute(query)
        return bool(result.scalar())

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
                full_name=mapped_cast(str, full_name),
                role=ShopRole(mapped_cast(str, role_name)),
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
            query = query.where(
                ShopMembership.name.ilike(f"%{escape_like(filters.name)}%")
            )

        query = apply_sorting(
            query, ShopMembership.name, ShopMembership.user_id, pagination
        )

        result = await self._session.execute(query)
        rows = result.all()

        return [
            EmployeeReadModel(
                user_id=UserId(mapped_cast(UUID, row[0])),
                full_name=mapped_cast(str, row[1]),
                role=ShopRole(mapped_cast(str, row[2])),
            )
            for row in rows
        ]

    def next_id(self) -> ShopId:
        return ShopId(uuid7())

    async def load_shop(self, shop_id: ShopId) -> Shop | None:
        query = select(Shop).where(Shop.id == shop_id)
        result = await self._session.execute(query)
        return result.scalar_one_or_none()

    async def get_shop_name(self, shop_id: ShopId) -> str | None:
        query = select(Shop.name).where(Shop.id == shop_id)
        result = await self._session.execute(query)
        return result.scalar_one_or_none()
