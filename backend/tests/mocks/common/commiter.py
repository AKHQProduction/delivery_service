from application.common.transaction_manager import TransactionManager


class FakeCommiter(TransactionManager):
    def __init__(self):
        self.commited = False

    async def commit(self) -> None:
        self.commited = True
