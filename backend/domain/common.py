from datetime import datetime, timezone
from typing import Generic, TypeVar

from pydantic import BaseModel, Field

from backend.domain.enums import SourceType, VerificationStatus

T = TypeVar("T")


class SourceReference(BaseModel):
    source_type: SourceType

    source_id: str | None = None
    source_field: str | None = None

    imported_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class SourcedValue(BaseModel, Generic[T]):
    value: T

    source: SourceReference

    verification_status: VerificationStatus = VerificationStatus.UNVERIFIED
