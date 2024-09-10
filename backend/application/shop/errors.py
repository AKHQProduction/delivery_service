from dataclasses import dataclass

from application.common.error import ApplicationError


@dataclass(eq=False)
class ShopTokenUnauthorizedError(ApplicationError):
    token: str

    @property
    def message(self):
        return f"Shop token {self.token} is unauthorized"


@dataclass(eq=False)
class ShopIsNotExistError(ApplicationError):
    shop_id: int

    @property
    def message(self):
        return f"Shop with id={self.shop_id} is not exists"


@dataclass(eq=False)
class UserNotHaveShopError(ApplicationError):
    user_id: int

    @property
    def message(self):
        return f"User {self.user_id} not have shop"


@dataclass(eq=False)
class ShopAlreadyExistError(ApplicationError):
    shop_id: int

    @property
    def message(self):
        return f"Shop with id={self.shop_id} already exists"


@dataclass(eq=False)
class ShopIsNotActive(ApplicationError):
    shop_id: int

    @property
    def message(self):
        return f"Shop={self.shop_id} is not active"
