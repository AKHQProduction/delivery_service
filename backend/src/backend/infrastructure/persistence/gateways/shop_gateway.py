from uuid import UUID

from sqlalchemy import exists, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from uuid_utils import uuid7

from backend.application.interfaces import ShopGateway
from backend.application.interfaces.gateways.shop_gateway import (
    CreateNewShopDTO,
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

    def next_id(self) -> ShopId:
        return ShopId(UUID(str(uuid7())))
