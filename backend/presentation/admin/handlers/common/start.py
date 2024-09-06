from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from dishka import FromDishka

from application.user.interactors.bot_start import BotStart, BotStartDTO
from application.common.identity_provider import IdentityProvider
from presentation.admin.keyboards.main_reply import MainReplyKeyboard

router = Router()


@router.message(CommandStart())
async def cmd_start(
        msg: Message,
        action: FromDishka[BotStart],
        id_provider: FromDishka[IdentityProvider],
):
    user_id: int = msg.from_user.id
    full_name: str = msg.from_user.full_name
    username: str | None = msg.from_user.username

    await action(
            BotStartDTO(
                    user_id=user_id,
                    full_name=full_name,
                    username=username
            )
    )

    await msg.answer(
            text=f"Hello, {full_name}",
            reply_markup=(
                await MainReplyKeyboard().render_keyboard()
            )
    )
