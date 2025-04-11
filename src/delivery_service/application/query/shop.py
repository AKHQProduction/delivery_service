import logging
from collections.abc import Sequence
from dataclasses import dataclass

from bazario.asyncio import RequestHandler

from delivery_service.application.common.markers.requests import (
    TelegramRequest,
)
from delivery_service.application.ports.idp import IdentityProvider
from delivery_service.application.query.ports.staff_gateway import (
    StaffGatewayFilters,
    StaffMemberGateway,
    StaffReadModel,
)
from delivery_service.domain.shared.errors import AccessDeniedError
from delivery_service.domain.shared.shop_id import ShopID
from delivery_service.domain.staff.repository import StaffMemberRepository

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class GetShopIDRequest(TelegramRequest[ShopID]):
    pass


class GetShopIDHandler(RequestHandler[GetShopIDRequest, ShopID]):
    def __init__(
        self,
        idp: IdentityProvider,
        staff_repository: StaffMemberRepository,
    ) -> None:
        self._idp = idp
        self._staff_repository = staff_repository

    async def handle(self, request: GetShopIDRequest) -> ShopID:
        logger.info("Request to get current staff shop id")
        current_user_id = await self._idp.get_current_user_id()

        staff_member = await self._staff_repository.load_with_identity(
            user_id=current_user_id
        )
        if not staff_member:
            raise AccessDeniedError()

        return staff_member.from_shop


@dataclass(frozen=True)
class GetShopStaffResponse:
    staff: Sequence[StaffReadModel]
    total: int


@dataclass(frozen=True)
class GetShopStaffMembersRequest(TelegramRequest[GetShopStaffResponse]):
    pass


class GetShopStaffMembersHandler(
    RequestHandler[GetShopStaffMembersRequest, GetShopStaffResponse]
):
    def __init__(
        self,
        idp: IdentityProvider,
        staff_repository: StaffMemberRepository,
        staff_gateway: StaffMemberGateway,
    ) -> None:
        self._idp = idp
        self._staff_repository = staff_repository
        self._staff_gateway = staff_gateway

    async def handle(
        self, request: GetShopStaffMembersRequest
    ) -> GetShopStaffResponse:
        logger.info("Request to get staff members")
        current_user_id = await self._idp.get_current_user_id()

        staff_member = await self._staff_repository.load_with_identity(
            user_id=current_user_id
        )
        if not staff_member:
            raise AccessDeniedError()

        filters = StaffGatewayFilters(shop_id=staff_member.from_shop)
        staff_members = await self._staff_gateway.read_all_staff(filters)
        total = await self._staff_gateway.total(filters)

        return GetShopStaffResponse(staff=staff_members, total=total)
