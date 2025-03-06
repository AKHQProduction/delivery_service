from uuid import UUID

from application.common.errors.employee import EmployeeNotFoundError
from application.common.errors.goods import GoodsNotFoundError
from application.common.errors.order import (
    OrderItemNotFoundError,
    OrderNotFoundError,
)
from application.common.errors.shop import (
    ShopIsNotActiveError,
    ShopNotFoundError,
)
from application.common.errors.user import UserNotFoundError
from entities.employee.models import Employee
from entities.goods.models import Goods
from entities.order.models import Order
from entities.shop.models import Shop
from entities.user.errors import UserIsNotActiveError
from entities.user.models import User


def validate_employee(employee: Employee | None) -> None:
    if not employee:
        raise EmployeeNotFoundError()


def validate_goods(goods: Goods | None, goods_id: UUID):
    if not goods:
        raise GoodsNotFoundError(goods_id)


def validate_shop(shop: Shop | None, *, must_be_active: bool = True):
    if not shop:
        raise ShopNotFoundError()
    if must_be_active and not shop.is_active:
        raise ShopIsNotActiveError()


def validate_user(user: User | None, *, must_be_active: bool = True):
    if not user:
        raise UserNotFoundError()
    if must_be_active and not user.is_active:
        raise UserIsNotActiveError(user.oid)


def validate_order(order: Order | None, order_id: int):
    if not order:
        raise OrderNotFoundError(order_id)


def validate_order_with_item(order: Order | None, order_item_id: int):
    if not any(item.oid != order_item_id for item in order.order_items):
        raise OrderItemNotFoundError(order_item_id)
