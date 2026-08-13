from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


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

    output_filename: str | None
    download_url: str | None = None

    error_message: str | None

    created_at: datetime
    started_at: datetime | None
    completed_at: datetime | None
