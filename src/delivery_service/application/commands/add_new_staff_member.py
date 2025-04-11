# ruff: noqa: E501
import logging
from dataclasses import dataclass

from bazario.asyncio import RequestHandler

from delivery_service.application.common.errors import ShopNotFoundError
from delivery_service.application.common.factories.staff_member_factory import (
    StaffMemberFactory,
)
from delivery_service.application.common.markers.requests import (
    BaseCommand,
    TelegramRequest,
)
from delivery_service.application.ports.idp import IdentityProvider
from delivery_service.application.ports.view_manager import ViewManager
from delivery_service.domain.shared.errors import AccessDeniedError
from delivery_service.domain.shared.shop_id import ShopID
from delivery_service.domain.shared.user_id import UserID
from delivery_service.domain.shops.access_service import ShopAccessService
from delivery_service.domain.shops.repository import (
    ShopRepository,
)
from delivery_service.domain.staff.staff_role import Role

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class AddNewStaffMemberRequest(BaseCommand[None]):
    candidate_id: UserID
    role: Role


class AddNewStaffMemberHandler(RequestHandler[AddNewStaffMemberRequest, None]):
    def __init__(
        self,
        identity_provider: IdentityProvider,
        shop_repository: ShopRepository,
        staff_member_factory: StaffMemberFactory,
        shop_access_service: ShopAccessService,
    ) -> None:
        self._idp = identity_provider
        self._shop_repository = shop_repository
        self._staff_member_factory = staff_member_factory
        self._shop_access_service = shop_access_service

    async def handle(self, request: AddNewStaffMemberRequest) -> None:
        logger.info("Request to add new staff member %s", request.candidate_id)
        current_user_id = await self._idp.get_current_user_id()

        shop = await self._shop_repository.load_with_identity(current_user_id)
        if not shop:
            raise ShopNotFoundError()

        current_user_roles = await self._idp.get_current_staff_roles()
        if not current_user_roles:
            raise AccessDeniedError()
        self._shop_access_service.can_add_staff_member(current_user_roles)

        new_staff_member = (
            await self._staff_member_factory.create_staff_member(
                user_id=request.candidate_id,
                shop_id=shop.entity_id,
                required_roles=[request.role],
            )
        )
        shop.add_staff_member(new_staff_member)


@dataclass(frozen=True)
class JoinStaffMemberRequest(TelegramRequest[None]):
    shop_id: ShopID


class JoinStaffMemberHandler(RequestHandler[JoinStaffMemberRequest, None]):
    def __init__(
        self,
        identity_provider: IdentityProvider,
        shop_repository: ShopRepository,
        staff_member_factory: StaffMemberFactory,
        view_manager: ViewManager,
    ) -> None:
        self._idp = identity_provider
        self._shop_repository = shop_repository
        self._staff_member_factory = staff_member_factory
        self._view_manager = view_manager

    async def handle(self, request: JoinStaffMemberRequest) -> None:
        logger.info("Request to join to shop new staff member")
        current_user_id = await self._idp.get_current_user_id()

        shop = await self._shop_repository.load_with_id(request.shop_id)
        if not shop:
            raise ShopNotFoundError()

        new_staff_member = (
            await self._staff_member_factory.create_staff_member(
                user_id=current_user_id,
                shop_id=shop.entity_id,
                required_roles=[Role.SHOP_MANAGER],
            )
        )
        shop.add_staff_member(new_staff_member)
        await self._view_manager.send_greeting_message(current_user_id)
