from enum import Enum

from pydantic import BaseModel, Field


class CustomerNeedCode(str, Enum):
    ACOUSTIC_NOISE = "acoustic_noise"
    THERMAL_LOSS = "thermal_loss"
    CONDENSATION = "condensation"
    VENTILATION = "ventilation"
    SECURITY = "security"
    PRIVACY = "privacy"
    LIGHT = "light"
    AESTHETICS = "aesthetics"


class CustomerNeedDefinition(BaseModel):
    code: CustomerNeedCode
    name: str

    description: str

    benefit_categories: list[str] = Field(default_factory=list)


class CustomerNeedSelection(BaseModel):
    code: CustomerNeedCode

    priority: int = Field(
        ge=1,
        le=5,
    )

    description: str | None = None

    source_text: str | None = None
