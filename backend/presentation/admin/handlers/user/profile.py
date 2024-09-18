from aiogram import F, Router
from aiogram.types import Message
from dishka import FromDishka

from application.common.identity_provider import IdentityProvider

router = Router()


@router.message(F.text == "👤 Профіль")
async def user_profile(
    msg: Message, id_provider: FromDishka[IdentityProvider]
):
    user = await id_provider.get_user()

    await msg.answer(
        "👤 <b>Ваш профіль</b> \n\n"
        f"🆔 <b>Ваш ID:</b> <code>{user.user_id}</code> \n"
        f"📞 <b>Ваш номер телефона:</b> {user.phone_number}",
    )
