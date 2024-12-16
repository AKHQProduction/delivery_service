from dataclasses import dataclass

from application.common.errors.base import ApplicationError


@dataclass(eq=False)
class ShopNotFoundError(ApplicationError):
    shop_id: int | None = None

    @property
    def message(self):
        return "Shop not found"


@dataclass(eq=False)
class UserNotHaveShopError(ApplicationError):
    user_id: int

    @property
    def message(self):
        return f"User {self.user_id} not have shop"


@dataclass(eq=False)
class ShopAlreadyExistsError(ApplicationError):
    shop_id: int

    @property
    def message(self):
        return f"Shop with id={self.shop_id} already exists"


@dataclass(eq=False)
class ShopIsNotActiveError(ApplicationError):
    shop_id: int | None = None

    @property
    def message(self):
        return "Shop is not active"
