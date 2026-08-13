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

from backend.db.models.reference_photo import (
    ReferencePhoto,
)
from backend.db.session import get_db
from backend.reference_photos.repository import (
    ReferencePhotoRepository,
)
from backend.reference_photos.schemas import (
    ReferencePhotoRead,
    ReferenceSelectionRead,
    ReferenceSelectionUpdate,
)
from backend.reference_photos.service import (
    ReferencePhotoService,
)
from backend.storage.reference import (
    ReferencePhotoStorage,
)

router = APIRouter(
    tags=["reference-photos"],
)

DbSession = Annotated[
    Session,
    Depends(get_db),
]


def _photo_read(
    photo: ReferencePhoto,
) -> ReferencePhotoRead:
    return ReferencePhotoRead(
        id=photo.id,
        filename=photo.original_filename,
        description=photo.description,
        problem_tags=photo.problem_tags,
        room_tags=photo.room_tags,
        window_type_tags=(photo.window_type_tags),
        feature_tags=photo.feature_tags,
        file_url=(f"/api/reference-photos/" f"{photo.id}/file"),
    )


def _selection_read(
    selection,
) -> ReferenceSelectionRead:
    return ReferenceSelectionRead(
        slot=selection.slot,
        status=selection.status,
        score=selection.score,
        photo=_photo_read(selection.reference_photo),
    )


@router.get(
    "/api/reference-photos",
    response_model=list[ReferencePhotoRead],
)
def list_reference_photos(
    db: DbSession,
) -> list[ReferencePhotoRead]:
    photos = ReferencePhotoRepository(db).list_active()

    return [_photo_read(photo) for photo in photos]


@router.get(
    "/api/reference-photos/" "{photo_id}/file",
)
def get_reference_photo_file(
    photo_id: uuid.UUID,
    db: DbSession,
) -> FileResponse:
    photo = ReferencePhotoRepository(db).get(photo_id=photo_id)

    if photo is None:
        raise HTTPException(
            status_code=404,
            detail=("Reference photo not found"),
        )

    path = ReferencePhotoStorage().get_path(storage_key=(photo.storage_key))

    if not path.exists():
        raise HTTPException(
            status_code=404,
            detail="Photo file not found",
        )

    return FileResponse(
        path,
        media_type=photo.content_type,
    )


@router.get(
    "/api/cases/{case_id}/" "reference-photos",
    response_model=list[ReferenceSelectionRead],
)
def get_case_reference_photos(
    case_id: uuid.UUID,
    db: DbSession,
) -> list[ReferenceSelectionRead]:
    service = ReferencePhotoService(db)

    selections = service.ensure_selections(case_id=case_id)

    return [_selection_read(selection) for selection in selections]


@router.post(
    "/api/cases/{case_id}/" "reference-photos/refresh",
    response_model=list[ReferenceSelectionRead],
)
def refresh_case_reference_photos(
    case_id: uuid.UUID,
    db: DbSession,
) -> list[ReferenceSelectionRead]:
    selections = ReferencePhotoService(db).refresh_suggestions(case_id=case_id)

    return [_selection_read(selection) for selection in selections]


@router.post(
    "/api/cases/{case_id}/" "reference-photos/confirm",
    response_model=list[ReferenceSelectionRead],
)
def confirm_case_reference_photos(
    case_id: uuid.UUID,
    db: DbSession,
) -> list[ReferenceSelectionRead]:
    selections = ReferencePhotoService(db).confirm_all(case_id=case_id)

    return [_selection_read(selection) for selection in selections]


@router.put(
    "/api/cases/{case_id}/" "reference-photos/{slot}",
    response_model=(ReferenceSelectionRead),
)
def select_reference_photo(
    case_id: uuid.UUID,
    slot: int,
    body: ReferenceSelectionUpdate,
    db: DbSession,
) -> ReferenceSelectionRead:
    try:
        selection = ReferencePhotoService(db).select_photo(
            case_id=case_id,
            slot=slot,
            photo_id=(body.reference_photo_id),
        )
    except (
        LookupError,
        ValueError,
    ) as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    return _selection_read(selection)


@router.delete(
    "/api/cases/{case_id}/" "reference-photos/{slot}",
    status_code=(status.HTTP_204_NO_CONTENT),
)
def remove_reference_photo(
    case_id: uuid.UUID,
    slot: int,
    db: DbSession,
) -> None:
    ReferencePhotoService(db).remove_selection(
        case_id=case_id,
        slot=slot,
    )


@router.post(
    "/api/cases/{case_id}/" "reference-photos/{slot}/upload",
    response_model=(ReferenceSelectionRead),
)
async def upload_reference_photo(
    case_id: uuid.UUID,
    slot: int,
    db: DbSession,
    file: Annotated[
        UploadFile,
        File(),
    ],
    description: Annotated[
        str | None,
        Form(),
    ] = None,
) -> ReferenceSelectionRead:
    content = await file.read()

    if not content:
        raise HTTPException(
            status_code=400,
            detail="Empty file",
        )

    content_type = file.content_type or "application/octet-stream"

    if not content_type.startswith("image/"):
        raise HTTPException(
            status_code=415,
            detail=("Only images are supported"),
        )

    storage = ReferencePhotoStorage()

    storage_key = storage.save(
        filename=(file.filename or "reference-photo"),
        content=content,
    )

    repository = ReferencePhotoRepository(db)

    photo = repository.add(
        ReferencePhoto(
            original_filename=(file.filename or "reference-photo"),
            storage_key=storage_key,
            content_type=content_type,
            description=description,
            problem_tags=[],
            room_tags=[],
            window_type_tags=[],
            feature_tags=[],
            active=True,
        )
    )

    selection = ReferencePhotoService(db).select_photo(
        case_id=case_id,
        slot=slot,
        photo_id=photo.id,
    )

    return _selection_read(selection)
