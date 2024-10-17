import logging
from dataclasses import dataclass, replace

from application.common.identity_provider import IdentityProvider
from application.employee.gateway import EmployeeGateway
from application.profile.data.output import UserProfileCardOutputData
from application.profile.errors import ProfileNotFoundError
from application.profile.gateway import ProfileReader
from application.shop.gateway import ShopGateway
from application.user.errors import UserNotFoundError
from application.user.gateway import UserReader
from entities.user.models import UserId


@dataclass(frozen=True)
class GetProfileCardInputData:
    user_id: int


@dataclass(frozen=True)
class GetProfileCard:
    identity_provider: IdentityProvider
    shop_reader: ShopGateway
    profile_reader: ProfileReader
    user_reader: UserReader
    employee_reader: EmployeeGateway

    async def __call__(
        self, data: GetProfileCardInputData
    ) -> UserProfileCardOutputData:
        user_id = UserId(data.user_id)

        user = await self.user_reader.by_id(user_id)
        if not user:
            raise UserNotFoundError(user_id)

        profile = await self.profile_reader.by_identity(user_id)
        if not profile:
            raise ProfileNotFoundError(user_id)

        profile_card = UserProfileCardOutputData(
            user_id=user_id,
            full_name=user.full_name,
            username=user.username,
            phone_number=profile.phone_number,
            address=profile.user_address.full_address,
        )

        if employee_data := await self.employee_reader.by_identity(user_id):
            profile_card = replace(
                profile_card,
                employee_id=employee_data.employee_id,
                role=employee_data.role,
            )

        logging.info("Get profile card for user_id=%s", data.user_id)

        return profile_card
