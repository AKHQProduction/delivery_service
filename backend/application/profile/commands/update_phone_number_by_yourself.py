import logging
from dataclasses import dataclass

from application.common.commiter import Commiter
from application.common.identity_provider import IdentityProvider
from application.profile.errors import ProfileNotFoundError
from application.profile.gateway import ProfileReader
from application.user.errors import UserNotFoundError


@dataclass
class UpdatePhoneNumberByYourselfInputData:
    phone_number: str


@dataclass
class UpdatePhoneNumberByYourself:
    identity_provider: IdentityProvider
    profile_reader: ProfileReader
    commiter: Commiter

    async def __call__(
        self, data: UpdatePhoneNumberByYourselfInputData
    ) -> None:
        actor = await self.identity_provider.get_user()
        if not actor:
            raise UserNotFoundError()

        profile = await self.profile_reader.by_identity(actor.user_id)
        if not profile:
            raise ProfileNotFoundError(actor.user_id)

        profile.phone_number = data.phone_number

        await self.commiter.commit()

        logging.info(
            "User with id=%s change him phone number to: %s",
            actor.user_id,
            data.phone_number,
        )
