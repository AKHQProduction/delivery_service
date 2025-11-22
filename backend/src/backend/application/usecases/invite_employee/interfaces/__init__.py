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
class Link:  # Like entity
    payload: str
    full_name: str
    role: ShopRole
    shop_id: ShopId


class LinkGateway(Protocol):
    @abstractmethod
    async def add(self, link: Link) -> None:
        raise NotImplementedError
