import logging
from dataclasses import dataclass, field

from application.common.access_service import AccessService
from application.common.commiter import Commiter
from application.common.identity_provider import IdentityProvider
from application.common.interactor import Interactor
from application.common.webhook_manager import WebhookManager
from application.employee.gateway import EmployeeSaver
from application.shop.gateway import ShopSaver
from application.user.errors import UserNotFoundError
from application.user.gateway import UserSaver
from entities.employee.models import Employee, EmployeeRole
from entities.shop.models import ShopId
from entities.shop.services import ShopService
from entities.shop.value_objects import ShopToken


@dataclass(frozen=True)
class CreateShopInputData:
    title: str
    token: str
    delivery_distance: int
    location: tuple[float, float]
    regular_days_off: list[int] = field(default_factory=list)


class CreateShop(Interactor[CreateShopInputData, ShopId]):
    def __init__(
        self,
        shop_saver: ShopSaver,
        user_saver: UserSaver,
        employee_saver: EmployeeSaver,
        commiter: Commiter,
        identity_provider: IdentityProvider,
        shop_service: ShopService,
        webhook_manager: WebhookManager,
        access_service: AccessService,
    ) -> None:
        self._shop_saver = shop_saver
        self._user_saver = user_saver
        self._employee_saver = employee_saver
        self._commiter = commiter
        self._identity_provider = identity_provider
        self._shop_service = shop_service
        self._webhook_manager = webhook_manager
        self._access_service = access_service

    async def __call__(self, data: CreateShopInputData) -> ShopId:
        user = await self._identity_provider.get_user()

        if not user:
            raise UserNotFoundError()

        await self._access_service.ensure_can_create_shop(user.user_id)

        shop = await self._shop_service.create_shop(
            user,
            data.title,
            data.token,
            data.regular_days_off,
            data.delivery_distance,
            data.location,
        )

        await self._shop_saver.save(shop)
        await self._employee_saver.save(
            Employee(
                employee_id=None,
                user_id=user.user_id,
                shop_id=shop.shop_id,
                role=EmployeeRole.ADMIN,
            ),
        )

        await self._webhook_manager.setup_webhook(ShopToken(data.token))

        await self._commiter.commit()

        logging.info(
            "CreateShop: User=%s created shop=%s", user.user_id, shop.shop_id
        )

        return shop.shop_id
