from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.orm import Session

from backend.cases.proposal_status import proposal_statuses_for_documents
from backend.db.session import get_db
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

DbSession = Annotated[Session, Depends(get_db)]


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
    db: DbSession,
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
        projects = service.search_projects(
            query=q,
            page=page,
            page_size=page_size,
        )
        statuses = proposal_statuses_for_documents(
            db, [(project.number, project.version) for project in projects]
        )
        return [
            {
                **project.model_dump(),
                "proposal_status": statuses[(project.number, project.version)],
            }
            for project in projects
        ]
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
