import logging
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
    AlreadyExistsError,
    AuthorizationError,
    EntityNotFoundError,
    PhoneNumberAlreadyExistsError,
    ValidationError,
)

if TYPE_CHECKING:

    class StubError(Exception):
        message: ClassVar[str]


logger = logging.getLogger(__name__)


async def validate(
    _: "Request", exc: Exception, status: int
) -> ORJSONResponse:
    exc = cast("StubError", exc)
    return ORJSONResponse(content={"detail": exc.message}, status_code=status)


async def internal_trouble(request: Request, exc: Exception) -> ORJSONResponse:
    logger.error(
        "Internal server error",
        extra={"path": request.url.path, "method": request.method},
    )
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
    app.add_exception_handler(
        ValidationError,
        partial(validate, status=code.HTTP_422_UNPROCESSABLE_CONTENT),
    )
    app.add_exception_handler(
        PhoneNumberAlreadyExistsError,
        partial(validate, status=code.HTTP_409_CONFLICT),
    )
    app.add_exception_handler(
        AlreadyExistsError,
        partial(validate, status=code.HTTP_409_CONFLICT),
    )
    app.exception_handler(Exception)(internal_trouble)
