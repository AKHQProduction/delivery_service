from typing import cast

from aiogram import F, Router
from aiogram.enums import ChatType
from aiogram.filters import CommandObject, CommandStart
from aiogram.types import Message, User
from aiogram.utils.payload import decode_payload
from aiogram_dialog import DialogManager, StartMode
from dishka import FromDishka

from backend.application.commands import (
    BotStartCommand,
    BotStartCommandHandler,
)
from backend.application.errors import (
    EntityNotFoundError,
    UserAlreadyRelatedToShopError,
)
from backend.application.usecases.invite_employee import (
    AcceptInviteCommand,
    AcceptInviteCommandHandler,
)
from backend.presentation.admin_bot import states
from backend.presentation.admin_bot.keyboards.inline import shop_kb

router = Router()


@router.message(CommandStart(deep_link=True), F.chat.type == ChatType.PRIVATE)
async def cmd_start_with_invite(
    message: Message,
    command: CommandObject,
    handler: FromDishka[AcceptInviteCommandHandler],
) -> Message:
    user: User = cast("User", message.from_user)
    if command.args:
        try:
            await handler.handle(
                AcceptInviteCommand(
                    payload=decode_payload(command.args),
                    tg_id=user.id,
                    full_name=user.full_name,
                )
            )
        except (EntityNotFoundError, UserAlreadyRelatedToShopError):
            return await message.answer("❌ Сталася помилка")
    return await message.answer(
        f"🙋 Привіт, {user.first_name}!", reply_markup=shop_kb()
    )


@router.message(CommandStart(), F.chat.type == ChatType.PRIVATE)
async def cmd_start(
    message: Message,
    dialog_manager: DialogManager,
    handler: FromDishka[BotStartCommandHandler],
) -> Message | None:
    user: User = cast("User", message.from_user)

    exists = await handler.handle(
        BotStartCommand(tg_id=user.id, full_name=user.full_name)
    )
    if exists:
        return await message.answer(
            f"🙋 Привіт, {user.first_name}!", reply_markup=shop_kb()
        )
    await dialog_manager.start(
        state=states.NewShop.NAME, mode=StartMode.RESET_STACK
    )
    return None
