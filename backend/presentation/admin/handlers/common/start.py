from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from dishka import FromDishka

from application.user.interactors.admin_bot_start import (
    AdminBotStart,
    AdminBotStartInputData,
)
from presentation.admin.keyboards.main_menu_kb import MainReplyKeyboard

router = Router()


@router.message(CommandStart())
async def cmd_start(
    msg: Message,
    action: FromDishka[AdminBotStart],
):
    user_id: int = msg.from_user.id
    full_name: str = msg.from_user.full_name
    username: str | None = msg.from_user.username

    output_data = await action(
        AdminBotStartInputData(
            user_id=user_id, full_name=full_name, username=username
        ),
    )

    await msg.answer(
        text=f"Hello, {full_name}",
        reply_markup=(
            await MainReplyKeyboard(output_data.role).render_keyboard()
        ),
    )
