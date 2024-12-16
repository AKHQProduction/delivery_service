from dataclasses import dataclass
from uuid import UUID

from application.common.errors.base import ApplicationError


@dataclass(eq=False)
class GoodsAlreadyExistsError(ApplicationError):
    title: str

    @property
    def message(self):
        return f"Goods with title={self.title} already exists"


@dataclass(eq=False)
class GoodsNotFoundError(ApplicationError):
    goods_id: UUID

    @property
    def message(self):
        return f"Goods with id={self.goods_id} is not exists"
