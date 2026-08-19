from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from backend.cloud.generation_launcher import (
    GenerationLauncher,
)
from backend.db.session import get_db
from backend.generation.schemas import (
    GenerationJobRead,
)
from backend.generation.service import (
    GenerationCaseNotFoundError,
    GenerationJobNotFoundError,
    GenerationJobService,
)
from backend.storage.generated import (
    GeneratedFileStorage,
)

router = APIRouter(
    tags=["generation"],
)

DbSession = Annotated[
    Session,
    Depends(get_db),
]


def _to_read(
    job,
) -> GenerationJobRead:
    download_url = None

    if job.status == "completed" and job.output_storage_key:
        download_url = f"/api/generation-jobs/" f"{job.id}/file"

    result = GenerationJobRead.model_validate(job)

    return result.model_copy(
        update={
            "download_url": download_url,
        }
    )


@router.post(
    "/api/cases/{case_id}/generation-jobs",
    response_model=GenerationJobRead,
    status_code=status.HTTP_202_ACCEPTED,
)
def create_generation_job(
    case_id: uuid.UUID,
    db: DbSession,
) -> GenerationJobRead:
    service = GenerationJobService(db)

    try:
        job = service.create_job(
            case_id=case_id,
        )

        GenerationLauncher().launch(
            job_id=job.id,
        )

    except GenerationCaseNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        if "job" in locals():
            service.mark_failed(
                job,
                error=(
                    "Could not launch "
                    "generation execution: "
                    f"{type(exc).__name__}: "
                    f"{exc}"
                ),
            )

        raise HTTPException(
            status_code=503,
            detail=("Could not launch " "generation execution"),
        ) from exc

    return _to_read(job)


@router.get(
    "/api/generation-jobs/{job_id}",
    response_model=GenerationJobRead,
)
def get_generation_job(
    job_id: uuid.UUID,
    db: DbSession,
) -> GenerationJobRead:
    service = GenerationJobService(db)

    try:
        job = service.get_job(
            job_id=job_id,
        )
    except GenerationJobNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    return _to_read(job)


@router.get(
    "/api/generation-jobs/{job_id}/file",
)
def get_generation_file(
    job_id: uuid.UUID,
    db: DbSession,
) -> FileResponse:
    service = GenerationJobService(db)

    try:
        job = service.get_job(
            job_id=job_id,
        )
    except GenerationJobNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    if job.status != "completed" or not job.output_storage_key:
        raise HTTPException(
            status_code=409,
            detail=("Presentation is not " "available yet"),
        )

    storage = GeneratedFileStorage()

    path = storage.get_path(
        storage_key=(job.output_storage_key),
    )

    if not path.exists():
        raise HTTPException(
            status_code=404,
            detail=("Generated file " "not found"),
        )

    return FileResponse(
        path=path,
        media_type=(
            "application/vnd."
            "openxmlformats-officedocument."
            "presentationml.presentation"
        ),
        filename=(job.output_filename or "SmartVitra.pptx"),
    )
