from dataclasses import dataclass

from application.common.interfaces.user.gateways import UserGateway
from application.common.transaction_manager import TransactionManager
from application.common.validators.shop import validate_shop
from application.shop.gateway import OldShopGateway
from application.user.errors import UserAlreadyExistError
from entities.shop.models import ShopId
from entities.shop.services import ShopService
from entities.user.models import UserId
from entities.user.services import UserService
from entities.user.value_objects import UserAddress


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
    user_service: UserService
    shop_service: ShopService
    user_gateway: UserGateway
    shop_gateway: OldShopGateway
    commiter: TransactionManager

    async def __call__(self, command: CreateUserCommand) -> UserId:
        if await self.user_gateway.is_exists(command.phone_number):
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
        new_user = self.user_service.create_new_user(
            command.full_name,
            address=address,
            phone_number=command.phone_number,
        )

        self.shop_service.add_user_to_shop(shop, new_user)

        await self.commiter.commit()

        return new_user.oid
