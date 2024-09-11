from aiogram import Router, F
from aiogram.types import Message
from dishka import FromDishka

from application.shop.interactors.change_regular_days_off import (
    ChangeRegularDaysOff,
    ChangeRegularDaysOffInputData
)
from application.shop.interactors.create_shop import (
    CreateShop,
    CreateShopInputData
)
from presentation.admin.consts import (
    CREATE_NEW_SHOP_TXT
)

router = Router()


@router.message(F.text == CREATE_NEW_SHOP_TXT)
async def create_new_shop_btn(
        msg: Message,

):
    await msg.answer(CREATE_NEW_SHOP_TXT)
