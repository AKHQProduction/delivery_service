import logging
from dataclasses import dataclass

from backend.application.errors import AlreadyExistsError
from backend.application.policies.access import (
    ensure_can_manage,
    ensure_related_to_shop,
)
from backend.application.vars import CategoryId
from backend.domain.services.category import update_category
from backend.domain.services.common import ensure_exists
from backend.infrastructure.idp import TelegramIdentityProvider
from backend.infrastructure.persistence.gateways import (
    SQLAlchemyCategoryGateway,
)
from backend.infrastructure.transaction_manager import TransactionManager

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class EditCategoryCommand:
    category_id: CategoryId
    new_name: str | None = None


class EditCategoryCommandHandler:
    def __init__(
        self,
        idp: TelegramIdentityProvider,
        category_gateway: SQLAlchemyCategoryGateway,
        tr_manager: TransactionManager,
    ) -> None:
        self._idp = idp
        self._category_gateway = category_gateway
        self._tr_manager = tr_manager

    async def handle(self, command: EditCategoryCommand) -> None:
        logger.info(
            "Editing category: category_id=%s, new_name=%s",
            command.category_id,
            command.new_name,
        )

        current_user = await self._idp.current_user()
        ensure_can_manage(current_user)

        category = ensure_exists(
            await self._category_gateway.load(command.category_id),
            "Category",
        )
        ensure_related_to_shop(current_user, category.shop_id)

        if command.new_name:
            if await self._category_gateway.exists_by_name_in_shop(
                command.new_name, current_user.shop_id
            ):
                raise AlreadyExistsError(entity="Category")
            update_category(category, name=command.new_name)

        await self._tr_manager.commit()

        logger.info(
            "Successfully edited category: id=%s, shop_id=%s",
            command.category_id,
            category.shop_id,
        )
