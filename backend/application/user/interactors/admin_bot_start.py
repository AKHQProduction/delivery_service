import logging
from dataclasses import dataclass

from application.common.commiter import Commiter
from application.common.identity_provider import IdentityProvider
from application.common.interactor import Interactor
from application.user.gateway import UserReader, UserSaver
from entities.employee.models import EmployeeRole
from entities.user.models import UserId
from entities.user.services import create_user


@dataclass(frozen=True)
class AdminBotStartInputData:
    user_id: int
    full_name: str
    username: str | None


@dataclass(frozen=True)
class AdminBotStartOutputData:
    role: EmployeeRole | None = None


class AdminBotStart(
    Interactor[AdminBotStartInputData, AdminBotStartOutputData]
):
    def __init__(
        self,
        user_reader: UserReader,
        user_saver: UserSaver,
        commiter: Commiter,
        identity_provider: IdentityProvider,
    ):
        self._user_reader = user_reader
        self._user_saver = user_saver
        self._commiter = commiter
        self._identity_provider = identity_provider

    async def __call__(
        self, data: AdminBotStartInputData
    ) -> AdminBotStartOutputData:
        actor = await self._identity_provider.get_user()
        role = await self._identity_provider.get_role()

        if not actor:
            user_id = UserId(data.user_id)

            await self._user_saver.save(
                create_user(user_id, data.full_name, data.username)
            )

            logging.info("New user created %s", data.user_id)

            await self._commiter.commit()

        return AdminBotStartOutputData(role=role)
