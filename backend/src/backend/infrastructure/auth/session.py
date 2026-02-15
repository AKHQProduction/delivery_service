from fastapi import Request

from backend.application.vars import UserId
from backend.infrastructure.persistence.gateways import RedisSessionGateway


class SessionAuthHandler:
    def __init__(self, session_gateway: RedisSessionGateway) -> None:
        self._session_gateway = session_gateway

    async def authenticate(self, request: Request) -> UserId | None:
        session_id = request.cookies.get("session_id")
        if not session_id:
            return None
        return await self._session_gateway.authenticate(session_id)
