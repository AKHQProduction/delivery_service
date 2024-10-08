from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from application.profile.errors import ProfileAlreadyExistError
from application.profile.gateway import (
    ProfileReader,
    ProfileSaver,
)
from entities.profile.models import Profile
from entities.shop.models import ShopId
from entities.user.models import UserId
from infrastructure.persistence.models.profile import profiles_table


class ProfileGateway(ProfileSaver, ProfileReader):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, profile: Profile) -> None:
        self.session.add(profile)

        try:
            await self.session.flush()
        except IntegrityError as error:
            raise ProfileAlreadyExistError(profile.profile_id) from error

    async def by_identity(self, user_id: UserId) -> Profile | None:
        query = select(Profile).where(profiles_table.c.user_id == user_id)

        result = await self.session.execute(query)

        return result.scalar_one_or_none()

    async def by_shop_id(
        self, user_id: UserId, shop_id: ShopId
    ) -> Profile | None:
        query = (
            select(Profile)
            .where(profiles_table.c.shop_id == shop_id)
            .where(profiles_table.c.user_id == user_id)
        )

        result = await self.session.execute(query)

        return result.scalar_one_or_none()
