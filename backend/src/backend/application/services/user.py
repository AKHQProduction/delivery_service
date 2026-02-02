from backend.application.vars import UserId
from backend.infrastructure.persistence.tables import TelegramAccount, User


def create_user_via_tg(
    *,
    user_id: UserId,
    tg_id: int,
    full_name: str,
) -> User:
    return User(
        id=user_id,
        telegram_account=TelegramAccount(
            telegram_id=tg_id, full_name=full_name
        ),
    )
