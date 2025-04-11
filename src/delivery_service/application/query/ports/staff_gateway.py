from abc import abstractmethod
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Protocol

from delivery_service.domain.shared.shop_id import ShopID
from delivery_service.domain.shared.user_id import UserID
from delivery_service.domain.staff.staff_role import Role


@dataclass(frozen=True)
class StaffReadModel:
    staff_id: UserID
    full_name: str
    roles: list[Role]


@dataclass(frozen=True)
class StaffGatewayFilters:
    shop_id: ShopID | None = None


class StaffMemberGateway(Protocol):
    @abstractmethod
    async def read_staff_member(
        self, user_id: UserID
    ) -> StaffReadModel | None:
        raise NotImplementedError

    @abstractmethod
    async def read_all_staff(
        self, filters: StaffGatewayFilters | None = None
    ) -> Sequence[StaffReadModel]:
        raise NotImplementedError

    @abstractmethod
    async def total(self, filters: StaffGatewayFilters | None = None) -> int:
        raise NotImplementedError
