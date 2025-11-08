from backend.application.interfaces import TransactionManager


class FakeTransactionManager(TransactionManager):
    def __init__(self) -> None:
        self.committed = False

    async def commit(self) -> None:
        self.committed = True
