from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from application.profile.errors import ProfileAlreadyExistError
from application.profile.gateway import ProfileSaver
from entities.profile.models import Profile


class ProfileGateway(ProfileSaver):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, profile: Profile) -> None:
        self.session.add(profile)

        try:
            await self.session.flush()
        except IntegrityError as error:
            raise ProfileAlreadyExistError(profile.profile_id) from error
