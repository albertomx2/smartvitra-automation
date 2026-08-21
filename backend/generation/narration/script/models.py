from __future__ import annotations

from pydantic import BaseModel, Field


class NarrationSlide(BaseModel):
    slide_number: int = Field(
        ge=1,
        le=9,
    )

    commercial_objective: str

    estimated_duration_seconds: int = Field(
        ge=5,
        le=60,
    )

    narration: str

    audio_duration_seconds: float | None = None


class NarrationScript(BaseModel):
    language: str = "es-ES"

    target_duration_seconds: int = 175

    estimated_duration_seconds: int

    word_count: int

    actual_duration_seconds: float | None = None

    slides: list[NarrationSlide] = Field(
        min_length=9,
        max_length=9,
    )

    @property
    def full_text(self) -> str:
        return "\n\n".join(slide.narration for slide in self.slides)
