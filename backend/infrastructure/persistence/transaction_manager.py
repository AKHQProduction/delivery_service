from sqlalchemy.ext.asyncio import AsyncSession

from application.common.transaction_manager import TransactionManager


class SATransactionManager(TransactionManager):
    def __init__(self, session: AsyncSession):
        self.session: AsyncSession = session

    async def commit(self) -> None:
        await self.session.commit()

    async def flush(self) -> None:
        await self.session.flush()
