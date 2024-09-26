from dataclasses import dataclass

from application.common.error import ApplicationError


@dataclass(eq=False)
class OrderItemIsNotExistError(ApplicationError):
    order_item_id: int

    @property
    def message(self):
        return f"Order item with id={self.order_item_id} is not exist"


@dataclass(eq=False)
class OrderIsNotExistError(ApplicationError):
    order_id: int

    @property
    def message(self):
        return f"Order with id={self.order_id} is not exist"
