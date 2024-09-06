from dataclasses import dataclass

from application.common.error import ApplicationError


@dataclass(eq=False)
class UserHasAlreadyCreatedShop(ApplicationError):
    shop_id: int

    @property
    def message(self):
        return f"User already has shop={self.shop_id}"


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
