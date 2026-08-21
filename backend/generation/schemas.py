from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class GenerationArtifactRead(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: uuid.UUID
    kind: str
    filename: str
    content_type: str
    size_bytes: int

    download_url: str | None = None


class GenerationJobRead(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: uuid.UUID
    case_id: uuid.UUID

    status: str
    current_step: str | None
    progress: int

    input_snapshot: dict[str, Any] | None

    # Legacy compatibility.
    output_filename: str | None
    download_url: str | None = None

    artifacts: list[GenerationArtifactRead] = Field(
        default_factory=list,
    )

    error_message: str | None

    created_at: datetime
    started_at: datetime | None
    completed_at: datetime | None
