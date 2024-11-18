from dataclasses import dataclass


@dataclass(frozen=True)
class UserAddress:
    city: str | None
    street: str | None
    house_number: str | None

    @property
    def full_address(self) -> str | None:
        if any([self.city, self.street]):
            return f"{self.city}, {self.street} {self.house_number}"
        return None


@dataclass(frozen=True)
class UserProfile:
    user_id: int
    full_name: str
    username: str | None
    tg_id: int | None
    phone_number: str | None
    address: UserAddress
