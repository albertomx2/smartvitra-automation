from pydantic import BaseModel, Field


class PresentationIssue(BaseModel):
    shape_name: str

    issue_type: str

    description: str

    severity: int = Field(
        ge=1,
        le=5,
    )


class PresentationQAResult(BaseModel):
    issues: list[PresentationIssue] = Field(default_factory=list)

    @property
    def is_valid(
        self,
    ) -> bool:
        return not any(issue.severity >= 4 for issue in self.issues)
