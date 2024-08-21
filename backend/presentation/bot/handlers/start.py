from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from dishka import FromDishka

from application.bot_start import BotStart, BotStartDTO
from application.common.identity_provider import IdentityProvider
from domain.entities.user import RoleName
from presentation.bot.keyboards.by_role import MainReplyKeyboard

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

    role: RoleName = await id_provider.get_user_role()

    await msg.answer(
            text=f"Hello, {full_name}",
            reply_markup=(
                await MainReplyKeyboard(role).render_keyboard()
            )
    )
