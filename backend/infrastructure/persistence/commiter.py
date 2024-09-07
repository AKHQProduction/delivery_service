from sqlalchemy.ext.asyncio import AsyncSession

from application.common.commiter import Commiter


class SACommiter(Commiter):
    def __init__(self, session: AsyncSession):
        self.session: AsyncSession = session

    async def commit(self) -> None:
        await self.session.commit()
