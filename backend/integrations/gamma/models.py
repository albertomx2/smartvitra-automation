from pydantic import BaseModel, Field


class GammaImageReference(BaseModel):
    role: str
    url: str

    opening_id: str | None = None


class GammaTemplateGenerationRequest(BaseModel):
    template_id: str

    prompt: str

    export_as: str = "pptx"

    theme_id: str | None = None

    folder_ids: list[str] = Field(default_factory=list)


class GammaGenerationJob(BaseModel):
    generation_id: str


class GammaGenerationResult(BaseModel):
    generation_id: str

    status: str

    gamma_url: str | None = None

    export_url: str | None = None

    credits_deducted: int | None = None

    credits_remaining: int | None = None
