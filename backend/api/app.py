from fastapi import FastAPI

from backend.api.cases import router as cases_router
from backend.api.generation import router as generation_router
from backend.api.reference_photos import router as reference_photos_router
from backend.api.routes.health import router as health_router
from backend.api.routes.prefweb import router as prefweb_router


def create_app() -> FastAPI:
    app = FastAPI(
        title="SmartVitra API",
        version="0.1.0",
        description="Backend API for the SmartVitra commercial workflow.",
    )

    app.include_router(health_router)
    app.include_router(
        prefweb_router,
        prefix="/api/prefweb",
    )

    app.include_router(
        cases_router,
    )

    app.include_router(generation_router)

    app.include_router(
        reference_photos_router,
    )

    return app


app = create_app()
