from uuid import UUID

from sqlalchemy import exists, select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid_utils import uuid7

from backend.application.interfaces import ShopGateway
from backend.application.interfaces.gateways.shop_gateway import (
    CreateNewShopDTO,
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
            name=dto.name,
            memberships=[ShopMembership(user_id=dto.user_id, role_id=role_id)],
        )

        self._session.add(new_shop)

    def next_id(self) -> ShopId:
        return ShopId(UUID(str(uuid7())))
