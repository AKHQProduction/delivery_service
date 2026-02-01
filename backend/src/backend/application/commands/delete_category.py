import logging
from dataclasses import dataclass

from backend.application.errors import AccessDeniedError
from backend.application.policies.access import (
    IsRelatedToShop,
    can_shop_manage_policy,
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
        logger.debug(
            "Current user: %s, shop_id=%s", current_user, current_user.shop_id
        )

        if not can_shop_manage_policy.is_satisfied_by(current_user):
            logger.warning(
                "Access denied for user %s when deleting category %s",
                current_user,
                command.category_id,
            )
            raise AccessDeniedError

        category = await self._category_gateway.load(command.category_id)
        if not category:
            logger.warning(
                "Category not found: category_id=%s", command.category_id
            )
            return

        if not IsRelatedToShop(category.shop_id).is_satisfied_by(current_user):
            logger.warning(
                "Access denied: user %s (shop_id=%s) attempted to delete "
                "category %s (shop_id=%s)",
                current_user,
                current_user.shop_id,
                command.category_id,
                category.shop_id,
            )
            raise AccessDeniedError

        await self._category_gateway.delete(category)
        await self._tr_manager.commit()

        logger.info(
            "Successfully deleted category: id=%s, shop_id=%s",
            command.category_id,
            category.shop_id,
        )
