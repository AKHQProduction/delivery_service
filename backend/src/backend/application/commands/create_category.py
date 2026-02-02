import logging
from dataclasses import dataclass

from backend.application.errors import AlreadyExistsError
from backend.application.policies.access import ensure_can_manage
from backend.application.services.category import create_category
from backend.application.vars import CategoryId
from backend.infrastructure.idp import TelegramIdentityProvider
from backend.infrastructure.persistence.gateways import (
    SQLAlchemyCategoryGateway,
)
from backend.infrastructure.transaction_manager import TransactionManager

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class CreateCategoryCommand:
    name: str


class CreateCategoryCommandHandler:
    def __init__(
        self,
        idp: TelegramIdentityProvider,
        gateway: SQLAlchemyCategoryGateway,
        tr_manager: TransactionManager,
    ) -> None:
        self._idp = idp
        self._gateway = gateway
        self._tr_manager = tr_manager

    async def handle(self, command: CreateCategoryCommand) -> CategoryId:
        logger.info("Creating category: name=%s", command.name)

        current_user = await self._idp.current_user()
        ensure_can_manage(current_user)

        if await self._gateway.exists_by_name_in_shop(
            command.name, current_user.shop_id
        ):
            raise AlreadyExistsError(entity="Category")

        category_id = self._gateway.next_id()

        category = create_category(
            category_id=category_id,
            shop_id=current_user.shop_id,
            name=command.name,
        )
        self._gateway.save(category)
        await self._tr_manager.commit()

        logger.info(
            "Successfully created category: id=%s, name=%s, shop_id=%s",
            category_id,
            command.name,
            current_user.shop_id,
        )
        return category_id
