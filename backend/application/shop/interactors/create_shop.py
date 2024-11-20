import logging
from dataclasses import dataclass, field

from application.common.access_service import AccessService
from application.common.commiter import Commiter
from application.common.identity_provider import IdentityProvider
from application.common.interactor import Interactor
from application.common.webhook_manager import WebhookManager
from application.employee.gateway import EmployeeGateway
from application.shop.gateway import ShopSaver
from application.user.errors import UserNotFoundError
from entities.employee.models import Employee, EmployeeRole
from entities.shop.models import ShopId
from entities.shop.services import add_user_to_shop, create_shop
from entities.shop.value_objects import ShopToken
from entities.user.errors import UserIsNotActiveError


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
        employee_saver: EmployeeGateway,
        commiter: Commiter,
        identity_provider: IdentityProvider,
        webhook_manager: WebhookManager,
        access_service: AccessService,
    ) -> None:
        self._shop_saver = shop_saver
        self._employee_saver = employee_saver
        self._commiter = commiter
        self._identity_provider = identity_provider
        self._webhook_manager = webhook_manager
        self._access_service = access_service

    async def __call__(self, data: CreateShopInputData) -> ShopId:
        actor = await self._identity_provider.get_user()
        if not actor:
            raise UserNotFoundError()
        if not actor.is_active:
            raise UserIsNotActiveError(actor.user_id)

        await self._access_service.ensure_can_create_shop(actor.user_id)

        await self._webhook_manager.setup_webhook(ShopToken(data.token))

        shop = create_shop(
            data.title,
            data.token,
            data.regular_days_off,
            data.delivery_distance,
            data.location,
        )

        add_user_to_shop(shop, actor)

        await self._shop_saver.save(shop)
        await self._employee_saver.save(
            Employee(
                employee_id=None,
                user_id=actor.user_id,
                shop_id=shop.shop_id,
                role=EmployeeRole.ADMIN,
            ),
        )

        await self._commiter.commit()

        logging.info(
            "CreateShop: User=%s created shop=%s", actor.user_id, shop.shop_id
        )

        return shop.shop_id
