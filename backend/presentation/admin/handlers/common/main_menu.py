from aiogram import Router, F
from aiogram.types import Message
from dishka import FromDishka

from application.employee.interactors.add_employee import (
    AddEmployee,
    AddEmployeeRequestData
)
from application.shop.interactors.change_regular_days_off import (

    ChangeRegularDaysOff,
    ChangeRegularDaysOffRequestData
)
from application.shop.interactors.create_shop import (
    CreateShop,
    CreateShopRequestData
)
from entities.employee.models import EmployeeRole
from presentation.admin.consts import (
    CREATE_NEW_SHOP_TXT
)

router = Router()


@router.message(F.text == CREATE_NEW_SHOP_TXT)
async def create_new_shop_btn(
        _: Message,
        create_shop: FromDishka[CreateShop],
        change_regular_days_off: FromDishka[ChangeRegularDaysOff],
        add_employee: FromDishka[AddEmployee]
):
    bot_token: str = "6668734619:AAFtjM-Q8M37k4I7pvJFWR602YuXHXh3Vto"
    bot_id: int = int(bot_token.split(":")[0])

    # await create_shop(
    #         CreateShopRequestData(
    #                 shop_id=bot_id,
    #                 title="TestShop",
    #                 token=bot_token
    #         )
    # )
    #
    # await change_regular_days_off(
    #         ChangeRegularDaysOffRequestData(
    #             shop_id=bot_id,
    #             regular_days_off=[5, 2]
    #             )
    # )

    await add_employee(
            AddEmployeeRequestData(
                    user_id=6696708679,
                    shop_id=bot_id,
                    role=EmployeeRole.MANAGER
            )
    )
