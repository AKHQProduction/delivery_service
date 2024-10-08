from dataclasses import dataclass


@dataclass(frozen=True)
class UserProfileCardOutputData:
    user_id: int
    full_name: str
    username: str | None
    phone_number: str | None
    address: str | None
