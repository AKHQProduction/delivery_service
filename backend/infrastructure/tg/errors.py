from dataclasses import dataclass


@dataclass(eq=False)
class ShopTokenUnauthorizedError(Exception):
    token: str

    @property
    def message(self):
        return f"Shop token {self.token} is unauthorized"
