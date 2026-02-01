from sqlalchemy.ext.asyncio import AsyncSession


class TransactionManager:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def commit(self) -> None:
        await self._session.commit()
