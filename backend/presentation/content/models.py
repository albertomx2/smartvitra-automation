from typing import Literal

from pydantic import BaseModel, Field

from backend.presentation.content.slide06 import (
    Slide06Content,
)
from backend.presentation.content.slide08 import (
    Slide08Content,
)
from backend.presentation.content.slide11 import (
    Slide11Content,
)
from backend.rendering.pptx.models import (
    SemanticColor,
)


class TextContent(BaseModel):
    shape_name: str

    text: str


class SemanticColorContent(BaseModel):
    slot: Literal[
        "s02_need_1",
        "s02_need_2",
        "s02_need_3",
        "s02_need_4",
    ]

    semantic_color: SemanticColor


class BenefitIconContent(BaseModel):
    benefit_index: int

    category: Literal[
        "thermal",
        "acoustic",
        "energy",
        "solar_control",
        "daylight",
        "ventilation",
        "air_tightness",
        "security",
        "privacy",
        "durability",
        "maintenance",
        "home_value",
        "aesthetics",
        "comfort",
        "humidity",
        "weather_protection",
    ]

    icon_key: Literal[
        "thermal",
        "acoustic",
        "energy",
        "solar_control",
        "daylight",
        "ventilation",
        "air_tightness",
        "security",
        "privacy",
        "durability",
        "maintenance",
        "home_value",
        "aesthetics",
        "comfort",
        "humidity",
        "weather_protection",
    ]


class GeneratedPresentationContent(BaseModel):
    texts: list[TextContent] = Field(default_factory=list)

    semantic_colors: list[SemanticColorContent] = Field(default_factory=list)

    slide06: Slide06Content | None = None

    slide08: Slide08Content | None = None

    slide11: Slide11Content | None = None

    benefit_icons: list[BenefitIconContent] = Field(default_factory=list)
