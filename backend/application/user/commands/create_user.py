from dataclasses import dataclass

from application.common.commiter import Commiter
from application.common.interfaces.user.gateways import UserGateway
from application.common.validators.shop import validate_shop
from application.shop.gateway import ShopGateway
from application.user.errors import UserAlreadyExistError
from entities.shop.models import ShopId
from entities.shop.services import add_user_to_shop
from entities.user.models import UserId
from entities.user.services import create_user
from entities.user.value_objects import PhoneNumber, UserAddress


@dataclass(frozen=True)
class CreateUserCommand:
    shop_id: int
    full_name: str
    city: str
    street: str
    house_number: str
    apartment_number: int | None
    floor: int | None
    intercom_code: int | None
    phone_number: str


@dataclass
class CreateUserCommandHandler:
    user_gateway: UserGateway
    shop_gateway: ShopGateway
    commiter: Commiter

    async def __call__(self, command: CreateUserCommand) -> UserId:
        phone_number = PhoneNumber(command.phone_number)

        if await self.user_gateway.is_exists(phone_number):
            raise UserAlreadyExistError

        shop = await self.shop_gateway.by_id(ShopId(command.shop_id))
        validate_shop(shop)

        address = UserAddress(
            city=command.city,
            street=command.street,
            house_number=command.house_number,
            apartment_number=command.apartment_number,
            floor=command.floor,
            intercom_code=command.intercom_code,
        )
        new_user = create_user(
            command.full_name, address=address, phone_number=phone_number
        )

        await self.user_gateway.add_one(new_user)
        add_user_to_shop(shop, new_user)

        await self.commiter.commit()

        return new_user.user_id
