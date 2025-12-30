import logging
from dataclasses import dataclass

from backend.application.errors import AccessDeniedError, AlreadyExistsError
from backend.application.interfaces import (
    IdentityProvider,
    TransactionManager,
)
from backend.application.interfaces.gateways.category_gateway import (
    CategoryGateway,
    CreateCategoryDTO,
)
from backend.application.policies.access import can_shop_manage_policy
from backend.application.vars import CategoryId

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class CreateCategoryCommand:
    name: str


class CreateCategoryCommandHandler:
    def __init__(
        self,
        idp: IdentityProvider,
        gateway: CategoryGateway,
        tr_manager: TransactionManager,
    ) -> None:
        self._idp = idp
        self._gateway = gateway
        self._tr_manager = tr_manager

    async def handle(self, command: CreateCategoryCommand) -> CategoryId:
        logger.info("Creating category: name=%s", command.name)

        current_user = await self._idp.current_user()
        logger.debug(
            "Current user: %s, shop_id=%s", current_user, current_user.shop_id
        )

        if not can_shop_manage_policy.is_satisfied_by(current_user):
            logger.warning(
                "Access denied for user %s when creating category %s",
                current_user,
                command.name,
            )
            raise AccessDeniedError

        if await self._gateway.exists_by_name_in_shop(
            command.name, current_user.shop_id
        ):
            logger.warning(
                "Category with name '%s' already exists in shop %s",
                command.name,
                current_user.shop_id,
            )
            raise AlreadyExistsError(entity="Category")

        category_id = self._gateway.next_id()
        logger.debug("Generated category_id: %s", category_id)

        await self._gateway.create_category(
            CreateCategoryDTO(
                category_id=category_id,
                shop_id=current_user.shop_id,
                name=command.name,
            )
        )
        await self._tr_manager.commit()

        logger.info(
            "Successfully created category: id=%s, name=%s, shop_id=%s",
            category_id,
            command.name,
            current_user.shop_id,
        )
        return category_id
