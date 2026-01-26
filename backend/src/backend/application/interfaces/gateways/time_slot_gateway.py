from abc import abstractmethod
from dataclasses import dataclass
from datetime import time
from typing import Protocol

from backend.application.vars import ShopId, TimeSlotId


@dataclass
class TimeSlot:
    time_slot_id: TimeSlotId
    shop_id: ShopId
    start_time: time
    end_time: time
    label: str | None


@dataclass(frozen=True)
class CreateTimeSlotDTO:
    time_slot_id: TimeSlotId
    shop_id: ShopId
    start_time: time
    end_time: time
    label: str | None


@dataclass(frozen=True)
class TimeSlotReadModel:
    time_slot_id: TimeSlotId
    start_time: time
    end_time: time
    label: str | None


class TimeSlotGateway(Protocol):
    @abstractmethod
    def next_id(self) -> TimeSlotId:
        raise NotImplementedError

    @abstractmethod
    async def create(self, dto: CreateTimeSlotDTO) -> None:
        raise NotImplementedError

    @abstractmethod
    async def load(self, time_slot_id: TimeSlotId) -> TimeSlot | None:
        raise NotImplementedError

    @abstractmethod
    async def load_by_shop(self, shop_id: ShopId) -> list[TimeSlotReadModel]:
        raise NotImplementedError

    @abstractmethod
    async def update(self, updated_time_slot: TimeSlot) -> None:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, time_slot_id: TimeSlotId) -> None:
        raise NotImplementedError

    @abstractmethod
    async def exists_by_times_in_shop(
        self, shop_id: ShopId, start_time: time, end_time: time
    ) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def count_by_shop(self, shop_id: ShopId) -> int:
        raise NotImplementedError
