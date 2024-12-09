from entities.common.tracker import Tracker
from entities.employee.services import EmployeeService
from entities.shop.models import Shop
from entities.shop.value_objects import (
    ShopLocation,
)
from entities.user.models import User


class ShopService:
    def __init__(self, tracker: Tracker, employee_service: EmployeeService):
        self.tracker = tracker
        self.employee_service = employee_service

    def create_shop(
        self,
        title: str,
        token: str,
        regular_days_off: list[int],
        delivery_distance: int,
        location: ShopLocation,
        user: User,
    ) -> Shop:
        shop_id = int(token.split(":")[0])

        new_shop = Shop(
            oid=shop_id,
            title=title,
            token=token,
            delivery_distance=delivery_distance,
            location=location,
            regular_days_off=regular_days_off,
        )

        self.tracker.add_one(new_shop)

        self.add_user_to_shop(new_shop, user)

        self.employee_service.add_employee(new_shop.oid, user.oid)

        return new_shop

    @staticmethod
    def add_user_to_shop(shop: Shop, new_user: User) -> None:
        if new_user not in shop.users:
            shop.users.append(new_user)
