from collections.abc import Sequence
from typing import Protocol

from fastapi import HTTPException, Request, status

from backend.application.vars import UserId


class AuthHandler(Protocol):
    async def authenticate(self, request: Request) -> UserId | None: ...


class AuthChain:
    def __init__(self, handlers: Sequence[AuthHandler]) -> None:
        self._handlers = handlers

    async def authenticate(self, request: Request) -> UserId:
        for handler in self._handlers:
            user_id = await handler.authenticate(request)
            if user_id is not None:
                return user_id
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
