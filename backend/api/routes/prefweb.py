from fastapi import APIRouter, HTTPException, Query, Response

from backend.integrations.prefweb.client import (
    PrefWebAuthenticationError,
)
from backend.integrations.prefweb.service import PrefWebService
from backend.integrations.prefweb.session import (
    prefweb_session_manager,
)

router = APIRouter(
    tags=["prefweb"],
)


def _service() -> PrefWebService:
    try:
        client = prefweb_session_manager.get_client()
        return PrefWebService(client)
    except PrefWebAuthenticationError as exc:
        prefweb_session_manager.reset()
        raise HTTPException(
            status_code=502,
            detail="Could not authenticate against PrefWeb",
        ) from exc
    except RuntimeError as exc:
        raise HTTPException(
            status_code=502,
            detail=str(exc),
        ) from exc


@router.get("/projects")
def search_projects(
    q: str = Query(
        default="",
        description="Optional customer, reference or budget search term.",
    ),
    page: int = Query(
        default=1,
        ge=1,
    ),
    page_size: int = Query(
        default=20,
        ge=1,
        le=100,
    ),
):
    service = _service()

    try:
        return service.search_projects(
            query=q,
            page=page,
            page_size=page_size,
        )
    except RuntimeError as exc:
        raise HTTPException(
            status_code=502,
            detail=str(exc),
        ) from exc


@router.get("/projects/{number}/versions")
def get_versions(
    number: int,
):
    service = _service()

    try:
        return service.get_versions(
            number=number,
        )
    except RuntimeError as exc:
        raise HTTPException(
            status_code=502,
            detail=str(exc),
        ) from exc


@router.get("/projects/{number}/versions/{version}")
def get_project(
    number: int,
    version: int,
):
    service = _service()

    try:
        return service.get_project_by_number(
            number=number,
            version=version,
        )
    except RuntimeError as exc:
        raise HTTPException(
            status_code=502,
            detail=str(exc),
        ) from exc


@router.get(
    "/projects/{number}/versions/{version}/windows/{item_id}/svg",
)
def get_window_svg(
    number: int,
    version: int,
    item_id: str,
) -> Response:
    service = _service()

    try:
        svg = service.get_window_svg(
            number=number,
            version=version,
            item_id=item_id,
        )
    except RuntimeError as exc:
        raise HTTPException(
            status_code=502,
            detail=str(exc),
        ) from exc

    return Response(
        content=svg,
        media_type="image/svg+xml",
    )
