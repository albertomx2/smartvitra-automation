from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.db.models.generation import (
    GenerationArtifact,
)


class GenerationArtifactRepository:
    def __init__(
        self,
        db: Session,
    ) -> None:
        self._db = db

    def add(
        self,
        artifact: GenerationArtifact,
    ) -> GenerationArtifact:
        self._db.add(artifact)
        self._db.commit()
        self._db.refresh(artifact)

        return artifact

    def list_for_job(
        self,
        *,
        generation_job_id: uuid.UUID,
    ) -> list[GenerationArtifact]:
        statement = (
            select(GenerationArtifact)
            .where(
                GenerationArtifact.generation_job_id == generation_job_id,
            )
            .order_by(
                GenerationArtifact.created_at,
            )
        )

        return list(self._db.scalars(statement).all())

    def get(
        self,
        *,
        artifact_id: uuid.UUID,
        generation_job_id: uuid.UUID,
    ) -> GenerationArtifact | None:
        statement = select(GenerationArtifact).where(
            GenerationArtifact.id == artifact_id,
            GenerationArtifact.generation_job_id == generation_job_id,
        )

        return self._db.scalar(statement)
