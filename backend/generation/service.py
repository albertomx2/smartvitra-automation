from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from backend.cases.repository import (
    CaseRepository,
)
from backend.db.models.generation import (
    GenerationJob,
)
from backend.generation.repository import (
    GenerationJobRepository,
)


class GenerationJobNotFoundError(LookupError):
    pass


class GenerationCaseNotFoundError(LookupError):
    pass


class GenerationJobService:
    def __init__(
        self,
        db: Session,
    ) -> None:
        self._jobs = GenerationJobRepository(db)

        self._cases = CaseRepository(db)

    def create_job(
        self,
        *,
        case_id: uuid.UUID,
    ) -> GenerationJob:
        case = self._cases.get(
            case_id=case_id,
        )

        if case is None:
            raise GenerationCaseNotFoundError(f"Case {case_id} not found")

        job = GenerationJob(
            case_id=case_id,
            status="queued",
            current_step="queued",
            progress=0,
        )

        return self._jobs.add(job)

    def get_job(
        self,
        *,
        job_id: uuid.UUID,
    ) -> GenerationJob:
        job = self._jobs.get(
            job_id=job_id,
        )

        if job is None:
            raise GenerationJobNotFoundError(f"Generation job " f"{job_id} not found")

        return job

    def mark_running(
        self,
        job: GenerationJob,
    ) -> None:
        job.status = "running"
        job.current_step = "loading_project"
        job.progress = 5
        job.started_at = datetime.now(timezone.utc)
        job.error_message = None

        self._jobs.commit()

    def update_progress(
        self,
        job: GenerationJob,
        *,
        step: str,
        progress: int,
    ) -> None:
        job.current_step = step
        job.progress = progress

        self._jobs.commit()

    def mark_completed(
        self,
        job: GenerationJob,
        *,
        storage_key: str,
        filename: str,
    ) -> None:
        job.status = "completed"
        job.current_step = "completed"
        job.progress = 100
        job.output_storage_key = storage_key
        job.output_filename = filename
        job.completed_at = datetime.now(timezone.utc)

        self._jobs.commit()

    def mark_failed(
        self,
        job: GenerationJob,
        *,
        error: str,
    ) -> None:
        job.status = "failed"
        job.current_step = "failed"
        job.error_message = error
        job.completed_at = datetime.now(timezone.utc)

        self._jobs.commit()
