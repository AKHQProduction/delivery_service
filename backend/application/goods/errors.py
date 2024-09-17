from dataclasses import dataclass
from uuid import UUID

from application.common.error import ApplicationError


@dataclass(eq=False)
class GoodsAlreadyExistError(ApplicationError):
    goods_id: UUID

    @property
    def message(self):
        return f"Goods with id={self.goods_id} already exists"
