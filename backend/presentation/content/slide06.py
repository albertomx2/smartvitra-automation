from pydantic import BaseModel, Field


class Slide06SolutionContent(BaseModel):
    lines: list[str] = Field(
        min_length=1,
        max_length=8,
    )


class Slide06Content(BaseModel):
    subtitle: str

    solutions: Slide06SolutionContent
