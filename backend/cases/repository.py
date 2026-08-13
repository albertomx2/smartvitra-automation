from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from backend.db.models import (
    CasePhoto,
    CaseWindow,
    ProjectCase,
)


class CaseRepository:
    def __init__(
        self,
        db: Session,
    ) -> None:
        self._db = db

    def get_by_prefweb_document(
        self,
        *,
        number: int,
        version: int,
    ) -> ProjectCase | None:
        statement = (
            select(ProjectCase)
            .options(
                selectinload(ProjectCase.windows).selectinload(CaseWindow.photos),
                selectinload(ProjectCase.photos),
            )
            .where(
                ProjectCase.prefweb_number == number,
                ProjectCase.prefweb_version == version,
            )
        )

        return self._db.scalar(statement)

    def get(
        self,
        *,
        case_id: uuid.UUID,
    ) -> ProjectCase | None:
        statement = (
            select(ProjectCase)
            .options(
                selectinload(ProjectCase.windows).selectinload(CaseWindow.photos),
                selectinload(ProjectCase.photos),
            )
            .where(
                ProjectCase.id == case_id,
            )
        )

        return self._db.scalar(statement)

    def get_windows(
        self,
        *,
        case_id: uuid.UUID,
    ) -> list[CaseWindow]:
        statement = (
            select(CaseWindow)
            .where(
                CaseWindow.case_id == case_id,
            )
            .order_by(
                CaseWindow.position,
            )
        )

        return list(self._db.scalars(statement).all())

    def get_window(
        self,
        *,
        case_id: uuid.UUID,
        window_id: uuid.UUID,
    ) -> CaseWindow | None:
        statement = select(CaseWindow).where(
            CaseWindow.id == window_id,
            CaseWindow.case_id == case_id,
        )

        return self._db.scalar(statement)

    def get_photo(
        self,
        *,
        case_id: uuid.UUID,
        photo_id: uuid.UUID,
    ) -> CasePhoto | None:
        statement = select(CasePhoto).where(
            CasePhoto.id == photo_id,
            CasePhoto.case_id == case_id,
        )

        return self._db.scalar(statement)

    def add_photo(
        self,
        photo: CasePhoto,
    ) -> CasePhoto:
        self._db.add(photo)
        self._db.commit()
        self._db.refresh(photo)

        return photo

    def delete_photo(
        self,
        photo: CasePhoto,
    ) -> None:
        self._db.delete(photo)
        self._db.commit()

    def list_photos(
        self,
        *,
        case_id: uuid.UUID,
    ) -> list[CasePhoto]:
        statement = (
            select(CasePhoto)
            .where(
                CasePhoto.case_id == case_id,
            )
            .order_by(
                CasePhoto.created_at,
            )
        )

        return list(self._db.scalars(statement).all())

    def add(
        self,
        case: ProjectCase,
    ) -> ProjectCase:
        self._db.add(case)
        self._db.commit()

        return (
            self.get(
                case_id=case.id,
            )
            or case
        )

    def commit(self) -> None:
        self._db.commit()

    def commit_and_refresh(
        self,
        instance,
    ) -> None:
        self._db.commit()
        self._db.refresh(instance)
