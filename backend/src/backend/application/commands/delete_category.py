import logging
from dataclasses import dataclass

from backend.application.policies.access import (
    ensure_can_manage,
    ensure_related_to_shop,
)
from backend.application.vars import CategoryId
from backend.infrastructure.idp import TelegramIdentityProvider
from backend.infrastructure.persistence.gateways import (
    SQLAlchemyCategoryGateway,
)
from backend.infrastructure.transaction_manager import TransactionManager

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class DeleteCategoryCommand:
    category_id: CategoryId


class DeleteCategoryCommandHandler:
    def __init__(
        self,
        idp: TelegramIdentityProvider,
        category_gateway: SQLAlchemyCategoryGateway,
        tr_manager: TransactionManager,
    ) -> None:
        self._idp = idp
        self._category_gateway = category_gateway
        self._tr_manager = tr_manager

    async def handle(self, command: DeleteCategoryCommand) -> None:
        logger.info(
            "Deleting category: category_id=%s",
            command.category_id,
        )

        current_user = await self._idp.current_user()
        ensure_can_manage(current_user)

        category = await self._category_gateway.load(command.category_id)
        if not category:
            return

        ensure_related_to_shop(current_user, category.shop_id)

        await self._category_gateway.delete(category)
        await self._tr_manager.commit()

        logger.info(
            "Successfully deleted category: id=%s, shop_id=%s",
            command.category_id,
            category.shop_id,
        )
