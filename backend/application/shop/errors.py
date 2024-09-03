from dataclasses import dataclass

from application.common.errors.base import ApplicationError


@dataclass(eq=False)
class UserHasAlreadyCreatedShop(ApplicationError):
    user_id: int

    @property
    def message(self):
        return f"User {self.user_id} already has shop"


@dataclass(eq=False)
class ShopTokenUnauthorizedError(ApplicationError):
    token: str

    @property
    def message(self):
        return f"Shop token {self.token} is unauthorized"


@dataclass(eq=False)
class ShopIsNotExistsError(ApplicationError):
    shop_id: int

    @property
    def message(self):
        return f"Shop with id={self.shop_id} is not exists"
