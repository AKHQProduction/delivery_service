import logging
from dataclasses import dataclass

from application.common.commiter import Commiter
from application.common.identity_provider import IdentityProvider
from application.profile.errors import ProfileNotFoundError
from application.profile.gateway import ProfileReader
from application.user.errors import UserNotFoundError
from entities.profile.value_objects import UserAddress


@dataclass(frozen=True)
class ChangeAddressInputData:
    city: str
    street: str
    house_number: str
    apartment_number: int | None
    floor: int | None
    intercom_code: int | None


@dataclass
class ChangeAddress:
    identity_provider: IdentityProvider
    profile_reader: ProfileReader
    commiter: Commiter

    async def __call__(self, data: ChangeAddressInputData):
        actor = await self.identity_provider.get_user()
        if not actor:
            raise UserNotFoundError()

        profile = await self.profile_reader.by_identity(actor.user_id)
        if not profile:
            raise ProfileNotFoundError(actor.user_id)

        profile.user_address = UserAddress(
            city=data.city,
            street=data.street,
            house_number=data.house_number,
            apartment_number=data.apartment_number,
            floor=data.floor,
            intercom_code=data.intercom_code,
        )

        await self.commiter.commit()

        logging.info(
            "Successfully updated user profile with id=%s", profile.user_id
        )
