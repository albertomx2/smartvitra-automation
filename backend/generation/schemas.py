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


class GenerationDeliveryRead(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: uuid.UUID
    generation_job_id: uuid.UUID

    status: str

    recipient_name: str
    recipient_email: str

    odoo_partner_id: int | None
    odoo_mail_id: int | None

    partner_created: bool
    attachment_count: int

    sent_artifacts: list[dict[str, Any]] | None
    error_message: str | None

    created_at: datetime
    sent_at: datetime | None


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

    latest_delivery: GenerationDeliveryRead | None = None

    error_message: str | None

    created_at: datetime
    started_at: datetime | None
    completed_at: datetime | None
