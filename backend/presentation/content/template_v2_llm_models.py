from pydantic import BaseModel, Field


class TemplateV2LLMIssue(BaseModel):
    keyword: str
    detail: str


class TemplateV2LLMSolution(BaseModel):
    text: str
    icon_key: str


class TemplateV2LLMSlide01(BaseModel):
    intro_text: str


class TemplateV2LLMSlide02(BaseModel):
    issues: list[TemplateV2LLMIssue] = Field(
        min_length=5,
        max_length=5,
    )

    impact_statement: str


class TemplateV2LLMSlide03(BaseModel):
    solutions: list[TemplateV2LLMSolution] = Field(
        min_length=1,
        max_length=6,
    )

    main_benefit: str
    secondary_benefit: str
    benefit_claim: str


class TemplateV2LLMSlide07(BaseModel):
    project_summary: list[str] = Field(
        min_length=1,
        max_length=5,
    )


class TemplateV2LLMContent(BaseModel):
    slide01: TemplateV2LLMSlide01
    slide02: TemplateV2LLMSlide02
    slide03: TemplateV2LLMSlide03
    slide07: TemplateV2LLMSlide07
