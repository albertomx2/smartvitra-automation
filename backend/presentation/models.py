from typing import Any

from pydantic import BaseModel, Field

from backend.presentation.enums import (
    SlideMode,
    SlideType,
)


class SlidePhotoReference(BaseModel):
    photo_id: str

    storage_key: str

    opening_id: str | None = None

    role: str

    is_ai_generated: bool = False


class PresentationSlide(BaseModel):
    position: int = Field(
        ge=1,
        le=12,
    )

    slide_type: SlideType

    mode: SlideMode

    title: str

    subtitle: str | None = None

    template_key: str | None = None

    locked: bool = False

    requires_ai_text: bool = False

    requires_generated_image: bool = False

    facts: dict[str, Any] = Field(default_factory=dict)

    photos: list[SlidePhotoReference] = Field(default_factory=list)


class PresentationSpec(BaseModel):
    proposal_number: str | None = None

    customer_name: str

    slides: list[PresentationSlide] = Field(default_factory=list)

    def get_slide(
        self,
        slide_type: SlideType,
    ) -> PresentationSlide:
        for slide in self.slides:
            if slide.slide_type == slide_type:
                return slide

        raise KeyError(f"Slide not found: {slide_type}")
