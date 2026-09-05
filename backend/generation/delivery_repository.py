from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.db.models.generation import (
    GenerationDelivery,
)


class GenerationDeliveryRepository:
    def __init__(
        self,
        db: Session,
    ) -> None:
        self._db = db

    def add(
        self,
        delivery: GenerationDelivery,
    ) -> GenerationDelivery:
        self._db.add(delivery)
        self._db.commit()
        self._db.refresh(delivery)

        return delivery

    def commit(
        self,
    ) -> None:
        self._db.commit()

    def refresh(
        self,
        delivery: GenerationDelivery,
    ) -> None:
        self._db.refresh(delivery)

    def get_latest_for_job(
        self,
        *,
        generation_job_id: uuid.UUID,
    ) -> GenerationDelivery | None:
        statement = (
            select(GenerationDelivery)
            .where(
                GenerationDelivery.generation_job_id == generation_job_id,
            )
            .order_by(
                GenerationDelivery.created_at.desc(),
            )
            .limit(1)
        )

        return self._db.scalar(statement)

    def get_sent_for_job(
        self,
        *,
        generation_job_id: uuid.UUID,
    ) -> GenerationDelivery | None:
        statement = (
            select(GenerationDelivery)
            .where(
                GenerationDelivery.generation_job_id == generation_job_id,
                GenerationDelivery.status == "sent",
            )
            .order_by(
                GenerationDelivery.created_at.desc(),
            )
            .limit(1)
        )

        return self._db.scalar(statement)
