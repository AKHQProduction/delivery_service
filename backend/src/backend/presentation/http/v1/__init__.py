from fastapi import APIRouter, FastAPI

from backend.presentation.http.v1.routes.categories import (
    router as category_router,
)
from backend.presentation.http.v1.routes.clients import (
    router as client_router,
)
from backend.presentation.http.v1.routes.employee import (
    router as employee_router,
)
from backend.presentation.http.v1.routes.invite_employee import (
    router as link_router,
)
from backend.presentation.http.v1.routes.orders import router as order_router
from backend.presentation.http.v1.routes.products import (
    router as product_router,
)
from backend.presentation.http.v1.routes.users import router as user_router


def setup_v1_router(app: FastAPI) -> None:
    v1_router = APIRouter(prefix="/v1")

    v1_router.include_router(user_router)
    v1_router.include_router(product_router)
    v1_router.include_router(category_router)
    v1_router.include_router(link_router)
    v1_router.include_router(employee_router)
    v1_router.include_router(client_router)
    v1_router.include_router(order_router)

    app.include_router(v1_router)
