import logging

from backend.infrastructure.persistence.gateways import RedisSessionGateway

logger = logging.getLogger(__name__)


class LogoutCommandHandler:
    def __init__(self, session_gateway: RedisSessionGateway) -> None:
        self._session_gateway = session_gateway

    async def handle(self, session_id: str) -> None:
        await self._session_gateway.remove_session(session_id)
        logger.info("Session removed")
