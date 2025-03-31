from aiogram import Bot, Router
from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery, Message
from dishka import FromDishka

from application.commands.bot.admin_bot_start import (
    AdminBotStartCommand,
    AdminBotStartCommandHandler,
)
from application.common.identity_provider import IdentityProvider
from presentation.admin.keyboards.main_menu_kb import MainReplyKeyboard

router = Router()


@router.message(CommandStart())
async def cmd_start(
    msg: Message | CallbackQuery,
    bot: Bot,
    action: FromDishka[AdminBotStartCommandHandler],
    id_provider: FromDishka[IdentityProvider],
):
    tg_id: int = msg.from_user.id
    full_name: str = msg.from_user.full_name
    username: str | None = msg.from_user.username

    await action(
        AdminBotStartCommand(
            tg_id=tg_id, full_name=full_name, username=username
        ),
    )

    role = await id_provider.get_role()

    await bot.send_message(
        text=f"Hello, {full_name}",
        chat_id=tg_id,
        reply_markup=(await MainReplyKeyboard(role).render_keyboard()),
    )
