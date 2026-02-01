from abc import abstractmethod
from dataclasses import dataclass
from typing import Protocol

from backend.application.vars import ShopId, ShopRole


@dataclass(frozen=True)
class GeneratedLink:
    link: str
    payload: str


class InviteLinkGenerator(Protocol):
    @abstractmethod
    async def generate(self) -> GeneratedLink:
        raise NotImplementedError


@dataclass(frozen=True)
class Link:
    payload: str
    full_name: str
    role: ShopRole
    shop_id: ShopId
