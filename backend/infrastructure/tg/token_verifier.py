from aiogram import Bot
from aiogram.exceptions import TelegramUnauthorizedError

from application.shop.errors import ShopTokenUnauthorizedError
from entities.common.token_verifier import TokenVerifier
from entities.shop.value_objects import ShopToken


class TgTokenVerifier(TokenVerifier):
    async def verify_token(self, token: ShopToken) -> None:
        token = token.value

        new_bot = Bot(token=token)

        try:
            await new_bot.get_me()
        except TelegramUnauthorizedError:
            raise ShopTokenUnauthorizedError(token)
        else:
            await new_bot.session.close()
