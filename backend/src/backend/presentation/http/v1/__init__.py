from fastapi import APIRouter, FastAPI

from backend.presentation.http.v1.routes.auth import router as auth_router
from backend.presentation.http.v1.routes.categories import (
    router as category_router,
)
from backend.presentation.http.v1.routes.clients import (
    router as client_router,
)
from backend.presentation.http.v1.routes.districts import (
    router as district_router,
)
from backend.presentation.http.v1.routes.employee import (
    router as employee_router,
)
from backend.presentation.http.v1.routes.geocoding import (
    router as geocoding_router,
)
from backend.presentation.http.v1.routes.invite_employee import (
    router as link_router,
)
from backend.presentation.http.v1.routes.orders import router as order_router
from backend.presentation.http.v1.routes.payment_methods import (
    router as payment_method_router,
)
from backend.presentation.http.v1.routes.products import (
    router as product_router,
)
from backend.presentation.http.v1.routes.route import router as route_router
from backend.presentation.http.v1.routes.shop import router as shop_router
from backend.presentation.http.v1.routes.time_slots import (
    router as time_slot_router,
)


def setup_v1_router(app: FastAPI) -> None:
    v1_router = APIRouter(prefix="/v1")

    v1_router.include_router(auth_router)
    v1_router.include_router(product_router)
    v1_router.include_router(category_router)
    v1_router.include_router(district_router)
    v1_router.include_router(link_router)
    v1_router.include_router(employee_router)
    v1_router.include_router(client_router)
    v1_router.include_router(order_router)
    v1_router.include_router(route_router)
    v1_router.include_router(time_slot_router)
    v1_router.include_router(payment_method_router)
    v1_router.include_router(shop_router)
    v1_router.include_router(geocoding_router)

    app.include_router(v1_router)
