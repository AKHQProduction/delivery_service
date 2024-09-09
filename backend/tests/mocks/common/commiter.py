from application.common.commiter import Commiter


class FakeCommiter(Commiter):
    def __init__(self):
        self.commited = True

    async def commit(self) -> None:
        self.commited = True
