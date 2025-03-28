from sqlalchemy.ext.asyncio import AsyncSession

from delivery_service.application.ports.transaction_manager import (
    TransactionManager,
)


class SQLAlchemyTransactionManager(TransactionManager):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def commit(self) -> None:
        await self._session.commit()
