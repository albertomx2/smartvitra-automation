from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    BigInteger,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.db.base import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class ProjectCase(Base):
    __tablename__ = "project_cases"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    prefweb_number: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
    )

    prefweb_version: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    alias_number: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    customer_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="draft",
    )

    visit_notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
        onupdate=utc_now,
    )

    windows: Mapped[list[CaseWindow]] = relationship(
        back_populates="case",
        cascade="all, delete-orphan",
        order_by="CaseWindow.position",
    )

    photos: Mapped[list[CasePhoto]] = relationship(
        back_populates="case",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        UniqueConstraint(
            "prefweb_number",
            "prefweb_version",
            name="uq_project_case_prefweb_document",
        ),
    )


class CaseWindow(Base):
    __tablename__ = "case_windows"

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

    prefweb_item_id: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    prefweb_id_pos: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    position: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    room: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    problem_type: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    commercial_notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    case: Mapped[ProjectCase] = relationship(
        back_populates="windows",
    )

    photos: Mapped[list[CasePhoto]] = relationship(
        back_populates="window",
    )

    __table_args__ = (
        UniqueConstraint(
            "case_id",
            "prefweb_item_id",
            name="uq_case_window_prefweb_item",
        ),
    )


class CasePhoto(Base):
    __tablename__ = "case_photos"

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

    window_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "case_windows.id",
            ondelete="CASCADE",
        ),
        nullable=True,
        index=True,
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

    size_bytes: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
    )

    case: Mapped[ProjectCase] = relationship(
        back_populates="photos",
    )

    window: Mapped[CaseWindow | None] = relationship(
        back_populates="photos",
    )
