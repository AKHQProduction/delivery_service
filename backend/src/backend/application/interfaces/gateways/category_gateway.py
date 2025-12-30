from abc import abstractmethod
from dataclasses import dataclass
from typing import Protocol

from backend.application.interfaces.gateways import Pagination
from backend.application.vars import CategoryId, ShopId


@dataclass
class Category:
    category_id: CategoryId
    shop_id: ShopId
    name: str


@dataclass(frozen=True)
class CreateCategoryDTO:
    category_id: CategoryId
    shop_id: ShopId
    name: str


@dataclass(frozen=True)
class CategoryReadModel:
    category_id: CategoryId
    name: str


@dataclass(frozen=True)
class GetCategoriesFilters:
    shop_id: ShopId | None = None
    name: str | None = None


class CategoryGateway(Protocol):
    @abstractmethod
    async def create_category(self, dto: CreateCategoryDTO) -> None:
        raise NotImplementedError

    @abstractmethod
    async def load(self, category_id: CategoryId) -> Category | None:
        raise NotImplementedError

    @abstractmethod
    async def update(self, updated_category: Category) -> None:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, category_id: CategoryId) -> None:
        raise NotImplementedError

    @abstractmethod
    async def read_all(
        self, filters: GetCategoriesFilters, pagination: Pagination
    ) -> list[CategoryReadModel]:
        raise NotImplementedError

    @abstractmethod
    async def exists_by_name_in_shop(self, name: str, shop_id: ShopId) -> bool:
        raise NotImplementedError

    @abstractmethod
    def next_id(self) -> CategoryId:
        raise NotImplementedError
