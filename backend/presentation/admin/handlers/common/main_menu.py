from aiogram import Router, F
from aiogram.types import Message
from dishka import FromDishka

from application.shop.interactors.change_regular_days_off import (

    ChangeRegularDaysOff,
    ChangeRegularDaysOffDTO
)
from application.shop.interactors.create_shop import CreateShop, CreateShopDTO
from presentation.admin.consts import (
    CREATE_NEW_SHOP_TXT
)

router = Router()


@router.message(F.text == CREATE_NEW_SHOP_TXT)
async def create_new_shop_btn(
        _: Message,
        create_shop: FromDishka[CreateShop],
        change_regular_days_off: FromDishka[ChangeRegularDaysOff]
):
    bot_token: str = "6668734619:AAFtjM-Q8M37k4I7pvJFWR602YuXHXh3Vto"
    bot_id: int = int(bot_token.split(":")[0])

    await create_shop(
            CreateShopDTO(
                    shop_id=bot_id,
                    title="TestShop",
                    token=bot_token
            )
    )

    await change_regular_days_off(
            ChangeRegularDaysOffDTO(shop_id=bot_id, regular_days_off=[5, 2])
    )
