import logging
from dataclasses import dataclass, field

from application.common.commiter import Commiter
from application.common.identity_provider import IdentityProvider
from application.common.interactor import Interactor
from application.common.specification import Specification
from application.shop.errors import ShopIsNotExistsError
from application.shop.gateway import ShopReader, ShopSaver
from application.specs.has_role import HasRoleSpec
from application.errors.access import AccessDeniedError
from entities.shop.models.entity import ShopId
from entities.user.models.user import RoleName


@dataclass(frozen=True)
class ChangeRegularDaysOffDTO:
    shop_id: int
    regular_days_off: list[int] = field(default_factory=list)


class ChangeRegularDaysOff(Interactor[ChangeRegularDaysOffDTO, None]):
    def __init__(
            self,
            identity_provider: IdentityProvider,
            shop_reader: ShopReader,
            shop_saver: ShopSaver,
            commiter: Commiter
    ) -> None:
        self._identity_provider = identity_provider
        self._shop_reader = shop_reader
        self._shop_saver = shop_saver
        self._commiter = commiter

    async def __call__(self, data: ChangeRegularDaysOffDTO) -> None:
        user = await self._identity_provider.get_user()

        rule: Specification = HasRoleSpec(RoleName.ADMIN)

        if not rule.is_satisfied_by(user.role):
            logging.info(
                    "ChangeRegularDaysOff: access denied for user with "
                    f"id={user.user_id}"
            )
            raise AccessDeniedError()

        shop = await self._shop_reader.by_id(ShopId(data.shop_id))

        if not shop:
            raise ShopIsNotExistsError(data.shop_id)

        shop.regular_days_off = data.regular_days_off

        await self._commiter.commit()

        logging.info(
                "ChangeRegularDaysOff: successfully change regular days off "
                f"for shop={data.shop_id}"
        )
