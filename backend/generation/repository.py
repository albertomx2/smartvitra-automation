from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.db.models.generation import (
    GenerationJob,
)


class GenerationJobRepository:
    def __init__(
        self,
        db: Session,
    ) -> None:
        self._db = db

    def add(
        self,
        job: GenerationJob,
    ) -> GenerationJob:
        self._db.add(job)
        self._db.commit()
        self._db.refresh(job)

        return job

    def get(
        self,
        *,
        job_id: uuid.UUID,
    ) -> GenerationJob | None:
        return self._db.scalar(
            select(GenerationJob).where(
                GenerationJob.id == job_id,
            )
        )

    def get_next_queued(
        self,
    ) -> GenerationJob | None:
        statement = (
            select(GenerationJob)
            .where(
                GenerationJob.status == "queued",
            )
            .order_by(
                GenerationJob.created_at,
            )
            .with_for_update(
                skip_locked=True,
            )
            .limit(1)
        )

        return self._db.scalar(statement)

    def commit(
        self,
    ) -> None:
        self._db.commit()

    def refresh(
        self,
        job: GenerationJob,
    ) -> None:
        self._db.refresh(job)
