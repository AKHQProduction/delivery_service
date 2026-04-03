import logging
from dataclasses import dataclass
from datetime import time

from backend.application.errors import (
    AuthorizationError,
    UserAlreadyRelatedToShopError,
)
from backend.application.services.payment_method import create_payment_method
from backend.application.services.shop import create_shop
from backend.application.services.time_slot import create_time_slot
from backend.application.vars import ShopRole
from backend.infrastructure.idp import IdentityProvider
from backend.infrastructure.persistence.gateways import (
    SQLAlchemyPaymentMethodGateway,
    SQLAlchemyShopGateway,
    SQLAlchemyUserGateway,
)
from backend.infrastructure.persistence.gateways.time_slot_gateway import (
    SQLAlchemyTimeSlotGateway,
)
from backend.infrastructure.transaction_manager import TransactionManager

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class CreateShopCommand:
    name: str


DEFAULT_TIME_SLOTS: list[tuple[str, time, time]] = [
    ("Перша половина дня", time(9, 0), time(14, 0)),
    ("Друга половина дня", time(14, 0), time(21, 0)),
]

DEFAULT_PAYMENT_METHODS: list[str] = [
    "Готівка",
    "На рахунок",
    "Інше",
]


class CreateShopCommandHandler:
    def __init__(
        self,
        shop_gateway: SQLAlchemyShopGateway,
        user_gateway: SQLAlchemyUserGateway,
        identity_provider: IdentityProvider,
        tr_manager: TransactionManager,
        time_slot_gateway: SQLAlchemyTimeSlotGateway,
        payment_method_gateway: SQLAlchemyPaymentMethodGateway,
    ) -> None:
        self._shop_gateway = shop_gateway
        self._user_gateway = user_gateway
        self._identity_provider = identity_provider
        self._tr_manager = tr_manager
        self._time_slot_gateway = time_slot_gateway
        self._payment_method_gateway = payment_method_gateway

    async def handle(self, command: CreateShopCommand) -> None:
        logger.info("Creating shop: name=%s", command.name)
        user_id = await self._identity_provider.current_user_id()

        if not user_id:
            raise AuthorizationError

        if await self._shop_gateway.relate_to_shop(user_id):
            raise UserAlreadyRelatedToShopError

        user = await self._user_gateway.load_user_with_tg(user_id)
        if not user:
            raise AuthorizationError

        shop_id = self._shop_gateway.next_id()
        owner_role_id = await self._shop_gateway.get_role_id(ShopRole.OWNER)

        shop = create_shop(
            shop_id=shop_id,
            name=command.name,
            owner_user_id=user_id,
            owner_name=user.telegram_account.full_name,
            owner_role_id=owner_role_id,
        )
        self._shop_gateway.save(shop)

        for label, start, end in DEFAULT_TIME_SLOTS:
            ts = create_time_slot(
                time_slot_id=self._time_slot_gateway.next_id(),
                shop_id=shop_id,
                start_time=start,
                end_time=end,
                label=label,
            )
            self._time_slot_gateway.save(ts)

        for name in DEFAULT_PAYMENT_METHODS:
            pm = create_payment_method(
                payment_method_id=self._payment_method_gateway.next_id(),
                shop_id=shop_id,
                name=name,
            )
            self._payment_method_gateway.save(pm)

        await self._tr_manager.commit()
        logger.info(
            "Successfully created shop: id=%s, name=%s",
            shop_id,
            command.name,
        )
