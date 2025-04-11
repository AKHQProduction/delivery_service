import logging
from dataclasses import dataclass

from bazario.asyncio import RequestHandler

from delivery_service.application.common.errors import (
    ShopNotFoundError,
)
from delivery_service.application.common.markers.requests import BaseCommand
from delivery_service.application.ports.idp import IdentityProvider
from delivery_service.domain.shared.errors import AccessDeniedError
from delivery_service.domain.shared.user_id import UserID
from delivery_service.domain.shops.access_service import ShopAccessService
from delivery_service.domain.shops.repository import (
    ShopRepository,
)

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class DiscardStaffMemberRequest(BaseCommand[None]):
    staff_member_id: UserID


class DiscardStaffMemberHandler(
    RequestHandler[DiscardStaffMemberRequest, None]
):
    def __init__(
        self,
        identity_provider: IdentityProvider,
        shop_repository: ShopRepository,
        shop_access_service: ShopAccessService,
    ) -> None:
        self._identity_provider = identity_provider
        self._shop_repository = shop_repository
        self._shop_access_service = shop_access_service

    async def handle(self, request: DiscardStaffMemberRequest) -> None:
        logger.info(
            "Request to discard staff member %s", request.staff_member_id
        )
        current_user_id = await self._identity_provider.get_current_user_id()

        shop = await self._shop_repository.load_with_identity(current_user_id)
        if not shop:
            raise ShopNotFoundError()
        current_user_roles = (
            await self._identity_provider.get_current_staff_roles()
        )
        if not current_user_roles:
            raise AccessDeniedError()

        self._shop_access_service.can_remove_staff_member(current_user_roles)

        shop.discard_staff_member(
            staff_member_id=request.staff_member_id, firer_id=current_user_id
        )
