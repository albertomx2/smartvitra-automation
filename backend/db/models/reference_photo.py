from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import (
    JSONB,
    UUID,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from backend.db.base import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class ReferencePhoto(Base):
    """
    Real SmartVitra completed-work photograph.

    This is corporate reusable content and is
    independent from a particular sales case.
    """

    __tablename__ = "reference_photos"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    original_filename: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    storage_key: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        unique=True,
    )

    content_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # Controlled metadata used by the matcher.
    # Arrays are intentional for MVP flexibility.
    problem_tags: Mapped[list[str]] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
    )

    room_tags: Mapped[list[str]] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
    )

    window_type_tags: Mapped[list[str]] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
    )

    feature_tags: Mapped[list[str]] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
    )

    active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
    )

    selections: Mapped[list[CaseReferenceSelection]] = relationship(
        back_populates="reference_photo",
    )


class CaseReferenceSelection(Base):
    """
    A specific reference image selected for one
    commercial proposal.

    Slots 1..3 correspond directly to the three
    related-work image positions in the PPTX.
    """

    __tablename__ = "case_reference_selections"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    case_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "project_cases.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    slot: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    reference_photo_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "reference_photos.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    # suggested:
    # automatically selected by matcher.
    #
    # confirmed:
    # explicitly accepted/selected by commercial.
    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="suggested",
    )

    score: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
    )

    reference_photo: Mapped[ReferencePhoto] = relationship(
        back_populates="selections",
    )

    __table_args__ = (
        UniqueConstraint(
            "case_id",
            "slot",
            name="uq_case_reference_selection_slot",
        ),
    )
