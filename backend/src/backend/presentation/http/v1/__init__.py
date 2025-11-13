from fastapi import APIRouter, FastAPI

from backend.presentation.http.v1.routes.users import router as user_router


def setup_v1_router(app: FastAPI) -> None:
    v1_router = APIRouter(prefix="/v1")

    v1_router.include_router(user_router)

    app.include_router(v1_router)
