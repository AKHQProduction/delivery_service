from uuid import UUID

from aiogram import F, Router
from aiogram.filters import CommandObject, CommandStart
from aiogram.types import Message
from bazario.asyncio import Sender
from dishka import FromDishka

from delivery_service.application.commands.add_new_staff_member import (
    JoinStaffMemberRequest,
)
from delivery_service.application.commands.bot_start import BotStartRequest
from delivery_service.domain.shared.shop_id import ShopID

START_ROUTER = Router()


@START_ROUTER.message(
    CommandStart(deep_link=True, magic=F.args.startswith("add_staff_"))
)
async def join_to_shop_as_shop_manager(
    _: Message,
    sender: FromDishka[Sender],
    command: CommandObject,
) -> None:
    if command.args:
        shop_id = ShopID(UUID(command.args.split("add_staff_")[1]))

        await sender.send(JoinStaffMemberRequest(shop_id=shop_id))


@START_ROUTER.message(CommandStart())
async def cmd_start_handler(_: Message, sender: FromDishka[Sender]) -> None:
    await sender.send(BotStartRequest())
