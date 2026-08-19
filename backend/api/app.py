from __future__ import annotations

from pathlib import Path

from fastapi import Depends, FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from backend.api.auth import router as auth_router
from backend.api.cases import router as cases_router
from backend.api.generation import router as generation_router
from backend.api.reference_photos import (
    router as reference_photos_router,
)
from backend.api.routes.health import router as health_router
from backend.api.routes.prefweb import router as prefweb_router
from backend.auth.firebase import require_user

PROJECT_ROOT = Path(__file__).resolve().parents[2]
FRONTEND_DIST = PROJECT_ROOT / "frontend" / "dist"


def create_app() -> FastAPI:
    app = FastAPI(
        title="SmartVitra API",
        version="0.1.0",
        description=("Backend API for the SmartVitra " "commercial workflow."),
    )

    app.include_router(health_router)

    app.include_router(
        auth_router,
    )

    protected_dependencies = [
        Depends(require_user),
    ]

    app.include_router(
        prefweb_router,
        prefix="/api/prefweb",
        dependencies=protected_dependencies,
    )

    app.include_router(
        cases_router,
        dependencies=protected_dependencies,
    )

    app.include_router(
        generation_router,
        dependencies=protected_dependencies,
    )

    app.include_router(
        reference_photos_router,
        dependencies=protected_dependencies,
    )

    if FRONTEND_DIST.exists():
        assets_dir = FRONTEND_DIST / "assets"

        if assets_dir.exists():
            app.mount(
                "/assets",
                StaticFiles(
                    directory=assets_dir,
                ),
                name="frontend-assets",
            )

        @app.get(
            "/{full_path:path}",
            include_in_schema=False,
        )
        def frontend(
            full_path: str,
        ) -> FileResponse:
            requested = FRONTEND_DIST / full_path

            if (
                full_path
                and requested.is_file()
                and FRONTEND_DIST in requested.resolve().parents
            ):
                return FileResponse(requested)

            return FileResponse(FRONTEND_DIST / "index.html")

    return app


app = create_app()
