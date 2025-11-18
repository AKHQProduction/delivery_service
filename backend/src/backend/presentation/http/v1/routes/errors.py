from functools import partial
from typing import TYPE_CHECKING, ClassVar, cast

from fastapi import (
    FastAPI,
    Request,
    status as code,
)
from fastapi.responses import ORJSONResponse

from backend.application.errors import (
    AccessDeniedError,
    AuthorizationError,
    EntityNotFoundError,
)

if TYPE_CHECKING:

    class StubError(Exception):
        message: ClassVar[str]


async def validate(
    _: "Request", exc: Exception, status: int
) -> ORJSONResponse:
    exc = cast("StubError", exc)
    return ORJSONResponse(content={"detail": exc.message}, status_code=status)


async def internal_trouble(_: Request, __: Exception) -> ORJSONResponse:
    return ORJSONResponse(
        content={"detail": "Internal server error"},
        status_code=code.HTTP_500_INTERNAL_SERVER_ERROR,
    )


def setup_exc_handlers(app: FastAPI) -> None:
    app.add_exception_handler(
        AuthorizationError,
        partial(validate, status=code.HTTP_401_UNAUTHORIZED),
    )
    app.add_exception_handler(
        AccessDeniedError, partial(validate, status=code.HTTP_403_FORBIDDEN)
    )
    app.add_exception_handler(
        EntityNotFoundError, partial(validate, status=code.HTTP_404_NOT_FOUND)
    )
    app.exception_handler(Exception)(internal_trouble)
