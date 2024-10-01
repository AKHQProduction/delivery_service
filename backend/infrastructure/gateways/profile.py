from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from application.profile.errors import ProfileAlreadyExistError
from application.profile.gateway import ProfileReader, ProfileSaver
from entities.profile.models import Profile
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
