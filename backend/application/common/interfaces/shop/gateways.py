from asyncio import Protocol


class ShopGateway(Protocol):
    async def is_exists(self, token: str) -> bool:
        raise NotImplementedError
