from __future__ import annotations

import uuid
from pathlib import Path
from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    UploadFile,
    status,
)
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from backend.cloud.generation_launcher import (
    GenerationLauncher,
)
from backend.db.models.generation import (
    GenerationArtifact,
)
from backend.db.session import get_db
from backend.generation.artifact_repository import (
    GenerationArtifactRepository,
)
from backend.generation.delivery import (
    ProposalDeliveryError,
    ProposalDeliveryService,
)
from backend.generation.delivery_repository import (
    GenerationDeliveryRepository,
)
from backend.generation.repository import (
    GenerationJobRepository,
)
from backend.generation.schemas import (
    GenerationArtifactRead,
    GenerationDeliveryRead,
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
    db: Session,
) -> GenerationJobRead:
    download_url = None

    if job.status == "completed" and job.output_storage_key:
        download_url = f"/api/generation-jobs/" f"{job.id}/file"

    artifact_models = GenerationArtifactRepository(
        db,
    ).list_for_job(
        generation_job_id=job.id,
    )

    artifacts = [
        GenerationArtifactRead.model_validate(
            artifact,
        ).model_copy(
            update={
                "download_url": (
                    f"/api/generation-jobs/"
                    f"{job.id}/artifacts/"
                    f"{artifact.id}/file"
                )
            }
        )
        for artifact in artifact_models
    ]

    latest_delivery_model = GenerationDeliveryRepository(
        db,
    ).get_latest_for_job(
        generation_job_id=job.id,
    )

    latest_delivery = (
        GenerationDeliveryRead.model_validate(
            latest_delivery_model,
        )
        if latest_delivery_model is not None
        else None
    )

    result = GenerationJobRead.model_validate(
        job,
    )

    return result.model_copy(
        update={
            "download_url": download_url,
            "artifacts": artifacts,
            "latest_delivery": latest_delivery,
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

    return _to_read(job, db)


@router.get(
    "/api/cases/{case_id}/generation-jobs/latest",
    response_model=GenerationJobRead | None,
)
def get_latest_generation_job(
    case_id: uuid.UUID,
    db: DbSession,
) -> GenerationJobRead | None:
    job = GenerationJobRepository(
        db,
    ).get_latest_for_case(
        case_id=case_id,
    )

    if job is None:
        return None

    return _to_read(
        job,
        db,
    )


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

    return _to_read(job, db)


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


@router.get(
    "/api/generation-jobs/" "{job_id}/artifacts/" "{artifact_id}/file",
)
def get_generation_artifact_file(
    job_id: uuid.UUID,
    artifact_id: uuid.UUID,
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

    if job.status != "completed":
        raise HTTPException(
            status_code=409,
            detail=("Generation is not completed"),
        )

    artifact = GenerationArtifactRepository(
        db,
    ).get(
        artifact_id=artifact_id,
        generation_job_id=job.id,
    )

    if artifact is None:
        raise HTTPException(
            status_code=404,
            detail=("Generated artifact not found"),
        )

    storage = GeneratedFileStorage()

    path = storage.get_path(
        storage_key=artifact.storage_key,
    )

    if not path.exists():
        raise HTTPException(
            status_code=404,
            detail=("Generated artifact file " "not found"),
        )

    return FileResponse(
        path=path,
        media_type=artifact.content_type,
        filename=artifact.filename,
    )


@router.post(
    "/api/generation-jobs/{job_id}/artifacts",
    response_model=GenerationArtifactRead,
    status_code=status.HTTP_201_CREATED,
)
def upload_generation_artifact(
    job_id: uuid.UUID,
    db: DbSession,
    file: Annotated[
        UploadFile,
        File(),
    ],
) -> GenerationArtifactRead:
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

    if job.status != "completed":
        raise HTTPException(
            status_code=409,
            detail=(
                "Additional attachments can only " "be added to a completed generation"
            ),
        )

    original_filename = Path(file.filename or "attachment").name

    if not original_filename:
        raise HTTPException(
            status_code=400,
            detail="Attachment filename is required",
        )

    storage = GeneratedFileStorage()

    work_dir = storage.build_job_directory(
        case_id=job.case_id,
        job_id=job.id,
    )

    attachment_dir = work_dir / "manual_attachments"

    attachment_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    internal_filename = f"{uuid.uuid4().hex}_" f"{original_filename}"

    local_path = attachment_dir / internal_filename

    total_bytes = 0

    try:
        with local_path.open("wb") as output:
            while True:
                chunk = file.file.read(
                    1024 * 1024,
                )

                if not chunk:
                    break

                total_bytes += len(chunk)

                if total_bytes > 50 * 1024 * 1024:
                    raise HTTPException(
                        status_code=413,
                        detail=("Attachment exceeds " "the 50 MB limit"),
                    )

                output.write(chunk)

        if total_bytes == 0:
            raise HTTPException(
                status_code=400,
                detail="Attachment is empty",
            )

        content_type = file.content_type or "application/octet-stream"

        storage_key = storage.persist(
            path=local_path,
            content_type=content_type,
        )

        artifact = GenerationArtifactRepository(
            db,
        ).add(
            GenerationArtifact(
                generation_job_id=job.id,
                kind="attachment",
                filename=original_filename,
                storage_key=storage_key,
                content_type=content_type,
                size_bytes=total_bytes,
            )
        )

    finally:
        file.file.close()

    return GenerationArtifactRead.model_validate(
        artifact,
    ).model_copy(
        update={
            "download_url": (
                f"/api/generation-jobs/" f"{job.id}/artifacts/" f"{artifact.id}/file"
            )
        }
    )


@router.delete(
    "/api/generation-jobs/{job_id}/artifacts/{artifact_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_generation_artifact(
    job_id: uuid.UUID,
    artifact_id: uuid.UUID,
    db: DbSession,
) -> None:
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

    if job.status != "completed":
        raise HTTPException(
            status_code=409,
            detail=("Attachments can only be removed " "from a completed generation"),
        )

    repository = GenerationArtifactRepository(
        db,
    )

    artifact = repository.get(
        artifact_id=artifact_id,
        generation_job_id=job.id,
    )

    if artifact is None:
        raise HTTPException(
            status_code=404,
            detail="Attachment not found",
        )

    if artifact.kind != "attachment":
        raise HTTPException(
            status_code=409,
            detail=("Generated proposal artifacts " "cannot be removed manually"),
        )

    storage = GeneratedFileStorage()

    storage.delete(
        storage_key=artifact.storage_key,
    )

    repository.delete(
        artifact,
    )


@router.post(
    "/api/generation-jobs/{job_id}/send",
    response_model=GenerationDeliveryRead,
)
def send_generation_to_customer(
    job_id: uuid.UUID,
    db: DbSession,
) -> GenerationDeliveryRead:
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

    try:
        delivery = ProposalDeliveryService(
            db,
        ).send(
            job=job,
        )
    except ProposalDeliveryError as exc:
        raise HTTPException(
            status_code=409,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=("Could not send proposal: " f"{type(exc).__name__}: " f"{exc}"),
        ) from exc

    return GenerationDeliveryRead.model_validate(
        delivery,
    )
