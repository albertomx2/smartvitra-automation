from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
    status,
)
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from backend.cases.schemas import (
    CaseCreate,
    CasePhotoRead,
    CasePhotoUpdate,
    CaseWindowRead,
    CaseWindowUpdate,
    CaseWorkspaceRead,
    ProjectCaseRead,
    ProjectCaseUpdate,
)
from backend.cases.service import (
    CaseNotFoundError,
    CasePhotoNotFoundError,
    CaseWindowNotFoundError,
    ProjectCaseService,
)
from backend.db.session import get_db
from backend.storage.local import LocalFileStorage

router = APIRouter(
    prefix="/api/cases",
    tags=["cases"],
)

DbSession = Annotated[
    Session,
    Depends(get_db),
]


ALLOWED_IMAGE_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
    "image/heic",
    "image/heif",
}

MAX_PHOTO_SIZE_BYTES = 20 * 1024 * 1024


@router.post(
    "",
    response_model=ProjectCaseRead,
)
def create_case(
    body: CaseCreate,
    db: DbSession,
) -> ProjectCaseRead:
    service = ProjectCaseService(db)

    try:
        case = service.create_from_prefweb(
            number=body.prefweb_number,
            version=body.prefweb_version,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Could not load PrefWeb project: {exc}",
        ) from exc

    return ProjectCaseRead.model_validate(case)


@router.get(
    "/{case_id}",
    response_model=ProjectCaseRead,
)
def get_case(
    case_id: uuid.UUID,
    db: DbSession,
) -> ProjectCaseRead:
    service = ProjectCaseService(db)

    try:
        case = service.get_case(
            case_id=case_id,
        )
    except CaseNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    return ProjectCaseRead.model_validate(case)


@router.get(
    "/{case_id}/workspace",
    response_model=CaseWorkspaceRead,
)
def get_case_workspace(
    case_id: uuid.UUID,
    db: DbSession,
) -> CaseWorkspaceRead:
    service = ProjectCaseService(db)

    try:
        return service.get_workspace(
            case_id=case_id,
        )
    except CaseNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Could not build workspace: {exc}",
        ) from exc


@router.patch(
    "/{case_id}/windows/{window_id}",
    response_model=CaseWindowRead,
)
def update_window(
    case_id: uuid.UUID,
    window_id: uuid.UUID,
    body: CaseWindowUpdate,
    db: DbSession,
) -> CaseWindowRead:
    service = ProjectCaseService(db)

    try:
        window = service.update_window(
            case_id=case_id,
            window_id=window_id,
            problem_type=body.problem_type,
            commercial_notes=body.commercial_notes,
        )
    except CaseWindowNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    return CaseWindowRead.model_validate(window)


@router.patch(
    "/{case_id}",
    response_model=ProjectCaseRead,
)
def update_case(
    case_id: uuid.UUID,
    body: ProjectCaseUpdate,
    db: DbSession,
) -> ProjectCaseRead:
    service = ProjectCaseService(db)

    try:
        case = service.update_case(
            case_id=case_id,
            visit_notes=body.visit_notes,
        )
    except CaseNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    return ProjectCaseRead.model_validate(case)


@router.post(
    "/{case_id}/photos",
    response_model=CasePhotoRead,
    status_code=status.HTTP_201_CREATED,
)
async def upload_case_photo(
    case_id: uuid.UUID,
    db: DbSession,
    file: Annotated[UploadFile, File()],
    window_id: Annotated[uuid.UUID | None, Form()] = None,
    description: Annotated[str | None, Form()] = None,
) -> CasePhotoRead:
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Unsupported image type",
        )

    content = await file.read()

    if not content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Empty file",
        )

    if len(content) > MAX_PHOTO_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Image exceeds 20 MB",
        )

    storage = LocalFileStorage()

    storage_key = storage.save(
        case_id=case_id,
        filename=file.filename or "photo",
        content=content,
    )

    service = ProjectCaseService(db)

    try:
        photo = service.create_photo(
            case_id=case_id,
            window_id=window_id,
            original_filename=file.filename or "photo",
            storage_key=storage_key,
            content_type=file.content_type or "application/octet-stream",
            size_bytes=len(content),
            description=description,
        )
    except (CaseNotFoundError, CaseWindowNotFoundError) as exc:
        storage.delete(
            storage_key=storage_key,
        )

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    return CasePhotoRead.model_validate(photo)


@router.get(
    "/{case_id}/photos/{photo_id}/file",
)
def get_case_photo_file(
    case_id: uuid.UUID,
    photo_id: uuid.UUID,
    db: DbSession,
) -> FileResponse:
    service = ProjectCaseService(db)

    try:
        photo = service.get_photo(
            case_id=case_id,
            photo_id=photo_id,
        )
    except CasePhotoNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    storage = LocalFileStorage()

    path = storage.get_path(
        storage_key=photo.storage_key,
    )

    if not path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Photo file not found",
        )

    return FileResponse(
        path=path,
        media_type=photo.content_type,
        filename=photo.original_filename,
    )


@router.patch(
    "/{case_id}/photos/{photo_id}",
    response_model=CasePhotoRead,
)
def update_case_photo(
    case_id: uuid.UUID,
    photo_id: uuid.UUID,
    body: CasePhotoUpdate,
    db: DbSession,
) -> CasePhotoRead:
    service = ProjectCaseService(db)

    try:
        photo = service.update_photo(
            case_id=case_id,
            photo_id=photo_id,
            description=body.description,
        )
    except CasePhotoNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    return CasePhotoRead.model_validate(photo)


@router.delete(
    "/{case_id}/photos/{photo_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_case_photo(
    case_id: uuid.UUID,
    photo_id: uuid.UUID,
    db: DbSession,
) -> None:
    service = ProjectCaseService(db)

    try:
        photo = service.delete_photo(
            case_id=case_id,
            photo_id=photo_id,
        )
    except CasePhotoNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    storage = LocalFileStorage()

    storage.delete(
        storage_key=photo.storage_key,
    )
